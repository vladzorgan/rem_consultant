import asyncio
import logging

import httpx
from bs4 import BeautifulSoup
from typing import List
import re

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
    'Accept-Language': 'ru,en;q=0.9',
    'Connection': 'keep-alive',
    'Cookie': 'anon_id=20250129210628writ.5d6e; _ym_uid=1725694892935755750; _ym_d=1738173989; _ga=GA1.2.1480822773.1738173990; locale=ru_RU; sid=24a67c6f67b032ed9f2ea300323302; _gid=GA1.2.945314185.1739600623; auth_token=894c247871fc4bb5fbeafb7b58e011b0; _ga_KK9RGD935B=GS1.2.1739668054.7.1.1739672557.52.0.0; _gat=1; _ym_isad=1; city=ekb',
    'Content-Type': 'application/json;charset=utf-8',
}

service_centers = []

API_URL = 'http://api'

# logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")


# Функция для обработки одной страницы
async def process_url(url: str, client: httpx.AsyncClient):
    response = await client.get(url, headers=headers)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    # Извлекаем название города
    model_name = None
    title = soup.find("div", class_="title")
    if title:
        if title.get_text(strip=True):
            model_name = title.get_text(strip=True).replace("Выбрано устройство: ", "").strip()

    prices = []

    print(model_name)

    # for item in soup.find_all("li", class_="minicard-item js-results-item"):
    #     name = item.find("a", class_="title-link")
    #
    # return centers

async def save_all_prices(prices: List[dict]):
    timeout = httpx.Timeout(connect=5.0, read=10.0, write=10.0, pool=10.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
        tasks = []
        for price in prices:
            tasks.append(save_price_data(price, client))

        await asyncio.gather(*tasks)

async def save_price_data(price, client):
    price_data = {
        "price": price["price"],
        "device_model": price["device_model"]
    }

    try:
        price_data_response = await client.post(f"{API_URL}/api/repair-prices", json=price_data)
    except httpx.RequestError as e:
        logging.error(f"Request error for {price_data['device_model']}: {e}")
    except Exception as e:
        logging.error(f"Unexpected error for {price_data['device_model']}: {e}")

async def main():
    # Список начальных URL
    urls = [
        'https://pedant.ru/remont-apple/iphone-12pro',
    ]

    async with httpx.AsyncClient() as client:
        for url in urls:
            try:
                logging.info(f"Fetching service centers for URL: {url}")
                await process_url(url, client)
            except httpx.RequestError as e:
                logging.error(f"Request error for URL {url}: {e}")
            except Exception as e:
                logging.error(f"Unexpected error for URL {url}: {e}")


# Запуск главной асинхронной функции
if __name__ == "__main__":
    asyncio.run(main())
