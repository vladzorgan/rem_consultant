import asyncio
import logging
import random
import time

import httpx
from bs4 import BeautifulSoup
from typing import List
import re
from urllib.parse import urljoin, parse_qs, urlparse, unquote

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
    'Accept-Language': 'ru,en;q=0.9',
    'Connection': 'keep-alive',
    'Cookie': 'anon_id=20250129210628writ.5d6e; _ym_uid=1725694892935755750; _ym_d=1738173989; _ga=GA1.2.1480822773.1738173990; locale=ru_RU; sid=24a67c6f67b032ed9f2ea300323302; _gid=GA1.2.945314185.1739600623; auth_token=894c247871fc4bb5fbeafb7b58e011b0; _ga_KK9RGD935B=GS1.2.1739668054.7.1.1739672557.52.0.0; _gat=1; _ym_isad=1; city=ekb',
    'Content-Type': 'application/json;charset=utf-8',
    'Bearer': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE3Mzk2MDA2MjEsImV4cCI6MTczOTY4NzAyMSwidHlwZSI6MH0.xlKxm-OIPXLKrCYRdC0TaJy204NwYGhvPX5NmyiU-sU',
}

service_centers = []

API_URL = 'http://api'

# logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")

# Функция для получения всех ссылок пагинации
async def get_pagination_links(url: str, client: httpx.AsyncClient):
    response = await client.get(url, headers=headers)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    # Находим блок пагинации
    pagination = soup.find("div", class_="paging js-paging-block-pages")
    if not pagination:
        return [url]  # Если пагинации нет, возвращаем только текущий URL

    # Собираем все ссылки на страницы
    links = set()
    for link in pagination.find_all("a", class_="paging__page"):
        href = link.get("href")
        if href:
            links.add(urljoin(url, href))  # Преобразуем относительные ссылки в абсолютные

    return sorted(links)

# Функция для обработки одной страницы
async def process_url(url: str, client: httpx.AsyncClient):
    response = await client.get(url, headers=headers)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    # Извлекаем название города
    city_name = None
    breadcrumbs = soup.find("div", class_="breadcrumbs")
    if breadcrumbs:
        city_link = breadcrumbs.find("a")
        if city_link:
            city_name = city_link.get_text(strip=True)

    centers = []  # Список для хранения данных сервисных центров на текущей странице

    for item in soup.find_all("li", class_="minicard-item js-results-item"):
        name = item.find("a", class_="title-link")
        address = item.find("span", class_="address")
        phone = item.find("span", class_="js-phone")
        card_link_item = item.find("a", class_='title-link js-item-url')

        if card_link_item:
            card_link_href = card_link_item.get("href")
            if card_link_href:
                card_response = await client.get(card_link_href, headers=headers)
                card_response.raise_for_status()
                card_soup = BeautifulSoup(card_response.text, "html.parser")
                social_links = []

                card_site_item = card_soup.find("div", class_="service-website-value")
                if card_site_item:
                    card_site_href = card_site_item.find("a").text
                    social_links.append(card_site_href)
                else:
                    card_site_href = None

                social_links_list = card_soup.find_all("a", class_="js-service-social")
                for link in social_links_list:
                    href = link.get("href")
                    if href and "zoon.ru/redirect/" in href:
                        parsed_url = urlparse(href)
                        query_params = parse_qs(parsed_url.query)
                        if "to" in query_params:
                            social_url = unquote(query_params["to"][0])
                            social_links.append(social_url)

                reviews_data = []
                reviews = card_soup.find_all("li", class_="comment-item js-comment")
                for review in reviews:
                    if not review.find_parent("ul", class_="comment-item__children"):
                        author = review.get("data-author", "Анонимный пользователь")
                        rating_element = review.find('div', class_='z-stars z-stars--16')

                        if rating_element:
                            try:
                                rating_element_style = rating_element['style']
                                rating_value = rating_element_style.split(': ')[1]  # --rating: 3, получаем "3"
                                rating_value = int(rating_value.strip())  # Убираем пробелы
                            except (IndexError, ValueError) as e:
                                rating_value = None  # В случае ошибки при извлечении или преобразовании
                        else:
                            rating_value = None  # Если рейтинг не найден, устанавливаем None

                        text = review.find("span", class_="js-comment-content")
                        text = text.get_text(strip=True) if text else "Текст отзыва не указан"
                        reviews_data.append({
                            "author": author,
                            "rating": rating_value if rating_value else None,
                            "text": text
                        })

                centers.append({
                    "city": city_name if city_name else None,
                    "site": card_site_href,
                    "reviews": reviews_data,
                    "social_links": social_links,
                    "name": name.get_text(strip=True) if name else None,
                    "address": address.get_text(strip=True) if address else None,
                    "phone": phone["data-number"].replace("\xa0", " ") if phone and phone.has_attr("data-number") else None
                })

    return centers

async def save_service_centers_to_api(service_centers: List[dict]):
    timeout = httpx.Timeout(connect=5.0, read=10.0, write=10.0, pool=10.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
        tasks = []
        for center in service_centers:
            tasks.append(save_center_data(center, client))

        await asyncio.gather(*tasks)

def determine_link_type(link: str) -> str:
    # Если ссылка начинается с 'tel:', то это телефон
    if link.startswith('tel:'):
        return 'phone'

    # Если ссылка на сайт, определяем домен
    parsed_url = urlparse(link)

    # Примеры: если домен относится к соцсетям, возвращаем соответствующий тип
    if "facebook.com" in parsed_url.netloc:
        return 'facebook'
    elif "instagram.com" in parsed_url.netloc:
        return 'instagram'
    elif "t.me" in parsed_url.netloc:
        return 'telegram'
    elif "vk.com" in parsed_url.netloc:
        return 'vk'

    # Если это ссылка на сайт (например, имеет 'https://', 'www.' и т.д.)
    if parsed_url.scheme in ['http', 'https']:
        return 'website'

    # Если это другой тип ссылки, можно вернуть 'other'
    return 'other'

async def save_center_data(center, client):
    service_data = {
        "city_id": center["city"],
        "name": center["name"],
        "address": center["address"],
        "phone": center["phone"],
    }

    try:
        # Отправляем запрос на создание сервисного центра
        logging.info(f"Creating service center: {center['name']}...")
        service_center_response = await client.post(f"{API_URL}/api/service_centers", json=service_data)

        if service_center_response.status_code == 200:
            service_center = service_center_response.json()
            service_center_id = service_center['id']
            logging.info(f"Service center '{center['name']}' created with ID {service_center_id}")

            # 2. Ссылки на сервисный центр
            for link in center["social_links"]:
                logging.info(f"Adding social link for service center {center['name']}: {link}")
                await client.post(f"{API_URL}/api/service_center_links", json={"service_center_id": service_center_id, "type": determine_link_type(link), "link": link})

            # 3. Отзывы
            for review in center["reviews"]:
                review_data = {
                    "service_center_id": service_center_id,
                    "author": review["author"],
                    "rating": review["rating"],
                    "text": review["text"]
                }
                logging.info(f"Adding review for service center {center['name']} by {review['author']}")
                await client.post(f"{API_URL}/api/reviews", json=review_data)

            logging.info(f"Service center '{center['name']}' successfully saved and related data added!")

        else:
            logging.error(f"Failed to create service center '{center['name']}': {service_center_response.text}")

    except httpx.RequestError as e:
        logging.error(f"Request error for {center['name']}: {e}")
    except Exception as e:
        logging.error(f"Unexpected error for {center['name']}: {e}")

# Функция для обработки всех страниц пагинации
async def process_all_pages(start_url: str, client: httpx.AsyncClient):
    current_url = start_url
    logging.info(f"URL {current_url}")

    while current_url:
        logging.info(f"Processing URL: {current_url}")
        # Обрабатываем текущую страницу
        page_service_centers = await process_url(current_url, client)

        # Сохранение сервисных центров в API
        try:
            logging.info("Saving service centers to API...")
            await save_service_centers_to_api(page_service_centers)
        except Exception as e:
            logging.error(f"Error saving service centers to API: {e}")

        # Получаем ссылку на следующую страницу
        next_page_url = await get_next_page_link(current_url, client)

        # Переходим к следующей странице, если она есть
        if next_page_url:
            current_url = next_page_url
        else:
            current_url = None  # Если нет следующей страницы, завершаем

    return service_centers

# Функция для получения ссылки на следующую страницу
async def get_next_page_link(url: str, client: httpx.AsyncClient):
    # Запрашиваем страницу

    response = await client.get(url, headers=headers)
    response.raise_for_status()  # Проверка на успешный запрос
    soup = BeautifulSoup(response.text, "html.parser")

    # Находим блок пагинации
    pagination = soup.find("div", class_="paging js-paging-block-pages")

    if not pagination:
        return None  # Если пагинации нет, возвращаем None

    # Находим ссылку на следующую страницу
    next_page = pagination.find("a", class_="paging__control _next")

    # Если следующая страница активна, возвращаем ссылку на нее
    if next_page and "disabled" not in next_page.get("class", []):
        next_page_link = next_page.get("href")
        if next_page_link:
            return urljoin(url, next_page_link)  # Преобразуем ссылку в абсолютную

    return None  # Если следующей страницы нет, возвращаем None

async def main():
    # Список начальных URL
    urls = [
        #'https://zoon.ru/abakan/repair/type/sotovyh_telefonov/',
        # 'https://zoon.ru/ekb/repair/type/sotovyh_telefonov/',
        # 'https://zoon.ru/perm/repair/type/sotovyh_telefonov/',
        # 'https://zoon.ru/chelyabinsk/repair/type/sotovyh_telefonov/',
        # 'https://zoon.ru/samara/repair/type/sotovyh_telefonov/',
        # 'https://zoon.ru/nn/repair/type/sotovyh_telefonov/',
        # 'https://zoon.ru/kazan/repair/type/sotovyh_telefonov/',
        # 'https://zoon.ru/nsk/repair/type/sotovyh_telefonov/',
        # 'https://zoon.ru/spb/repair/type/sotovyh_telefonov/',
        # 'https://zoon.ru/msk/repair/type/sotovyh_telefonov/',
        # 'https://zoon.ru/omsk/repair/type/sotovyh_telefonov/',
        # 'https://zoon.ru/rostov/repair/type/sotovyh_telefonov/',
        # 'https://zoon.ru/ufa/repair/type/sotovyh_telefonov/',
        # 'https://zoon.ru/krasnoyarsk/repair/type/sotovyh_telefonov/',
        # 'https://zoon.ru/krasnodar/repair/type/sotovyh_telefonov/',
        # 'https://zoon.ru/voronezh/repair/type/sotovyh_telefonov/',
        # 'https://zoon.ru/volgograd/repair/type/sotovyh_telefonov/',
        # 'https://zoon.ru/elista/repair/type/sotovyh_telefonov/',
        # 'https://zoon.ru/stavropol/repair/type/sotovyh_telefonov/',
        # 'https://zoon.ru/cherkessk/repair/type/sotovyh_telefonov/',
        # 'https://zoon.ru/nalchik/repair/type/sotovyh_telefonov/',
        # 'https://zoon.ru/grozny/repair/type/sotovyh_telefonov/',
        # 'https://zoon.ru/sochi/repair/type/sotovyh_telefonov/',
        # 'https://zoon.ru/vladikavkaz/repair/type/sotovyh_telefonov/',
        # 'https://zoon.ru/astrakhan/repair/type/sotovyh_telefonov/'
    ]

    async with httpx.AsyncClient() as client:
        for url in urls:
            try:
                logging.info(f"Fetching service centers for URL: {url}")
                await process_all_pages(url, client)
            except httpx.RequestError as e:
                logging.error(f"Request error for URL {url}: {e}")
            except Exception as e:
                logging.error(f"Unexpected error for URL {url}: {e}")


# Запуск главной асинхронной функции
if __name__ == "__main__":
    asyncio.run(main())
