import logging

from telegram import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from typing import List, Dict, Any, Optional

from app.helpers import pluralize_reviews

logger = logging.getLogger(__name__)

# Константы для callback-префиксов
CALLBACK_REGION_PREFIX = "region_"
CALLBACK_CITY_PREFIX = "city_"
CALLBACK_CENTER_PREFIX = "center_"
CALLBACK_CENTER_PAGE_PREFIX = "center_page_"
CALLBACK_REVIEWS_PREFIX = "reviews_"
CALLBACK_PRICES_PREFIX = "prices_"
CALLBACK_CLAIM_SERVICE_PREFIX = "claim_service_"
CALLBACK_BACK_REGION = "back_region_list"
CALLBACK_BACK_CENTER = "back_center_list"
ITEMS_PER_PAGE = 5


def _build_inline_keyboard(
        items: List[Dict[str, Any]],
        label_key: str,
        callback_prefix: str,
        columns: int = 2,
        extra_buttons: Optional[List[InlineKeyboardButton]] = None
) -> InlineKeyboardMarkup:
    """
    Универсальная функция для построения inline-клавиатуры с заданным количеством колонок.

    Args:
        items: Список элементов для отображения
        label_key: Ключ словаря для текста кнопки
        callback_prefix: Префикс для callback_data
        columns: Количество кнопок в строке
        extra_buttons: Дополнительные кнопки в конце (опционально)

    Returns:
        InlineKeyboardMarkup с кнопками
    """
    keyboard = []
    for i in range(0, len(items), columns):
        row = [
            InlineKeyboardButton(
                items[i + j][label_key],
                callback_data=f"{callback_prefix}{items[i + j]['id']}"
            )
            for j in range(columns) if i + j < len(items)
        ]
        keyboard.append(row)

    if extra_buttons:
        keyboard.append(extra_buttons)

    return InlineKeyboardMarkup(keyboard)


# Reply-клавиатуры
def main_menu_keyboard() -> ReplyKeyboardMarkup:
    """Основное меню с кнопками и иконками"""
    keyboard = [
        [KeyboardButton("Сервисные центры 🛠️")],
        [KeyboardButton("Узнать цену ремонта 💰")],
        [KeyboardButton("Настройки пользователя ⚙️")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)


def user_settings_keyboard() -> ReplyKeyboardMarkup:
    """Меню настроек пользователя"""
    keyboard = [
        [KeyboardButton("Выбрать город по умолчанию 🌍")],
        [KeyboardButton("Управление сервисом 🛠️")],
        [KeyboardButton("Назад 🔙")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)


# Inline-клавиатуры
def regions_keyboard(regions: List[Dict[str, Any]]) -> InlineKeyboardMarkup:
    """Клавиатура для выбора региона (inline, 2 колонки)"""
    return _build_inline_keyboard(
        items=regions,
        label_key="name",
        callback_prefix=CALLBACK_REGION_PREFIX,
        columns=2
    )


def cities_keyboard(cities: List[Dict[str, Any]]) -> InlineKeyboardMarkup:
    """Клавиатура для выбора города (inline, 2 колонки)"""
    back_button = [InlineKeyboardButton("Назад", callback_data=CALLBACK_BACK_REGION)]
    return _build_inline_keyboard(
        items=cities,
        label_key="name",
        callback_prefix=CALLBACK_CITY_PREFIX,
        columns=2,
        extra_buttons=back_button
    )


def service_centers_keyboard(
        service_centers: List[Dict[str, Any]],
        page: int = 0,
        items_per_page: int = ITEMS_PER_PAGE
) -> InlineKeyboardMarkup:
    """Клавиатура для выбора сервисных центров с пагинацией"""
    keyboard = []

    for center in service_centers:
        button_text = f"{center['name']} ⭐️{center.get('avg_rating', 0)} ({center.get('reviews_count', 0)})"
        keyboard.append([
            InlineKeyboardButton(button_text, callback_data=f"{CALLBACK_CENTER_PREFIX}{center['id']}")
        ])

    # Пагинация
    navigation_buttons = []
    if page > 0:
        navigation_buttons.append(
            InlineKeyboardButton("⬅️ Назад", callback_data=f"{CALLBACK_CENTER_PAGE_PREFIX}{page - 1}")
        )
    if len(service_centers) == items_per_page:
        navigation_buttons.append(
            InlineKeyboardButton("Вперед ➡️", callback_data=f"{CALLBACK_CENTER_PAGE_PREFIX}{page + 1}")
        )

    if navigation_buttons:
        keyboard.append(navigation_buttons)

    return InlineKeyboardMarkup(keyboard)


def service_centers_buttons_keyboard(service_center_id: int, is_owner: bool = False) -> InlineKeyboardMarkup:
    """Клавиатура с кнопками для сервисного центра"""
    back_data = f"back_to_list_"
    logger.debug(f"Back data={back_data}")

    keyboard = [
        [InlineKeyboardButton("Отзывы 📝", callback_data=f"{CALLBACK_REVIEWS_PREFIX}{service_center_id}")],
        [InlineKeyboardButton("Прайс-лист 💰", callback_data=f"{CALLBACK_PRICES_PREFIX}{service_center_id}")],
    ]

    if is_owner is False:
        manage_button = InlineKeyboardButton(
            "Это мой сервис 🛠️",
            callback_data=f"{CALLBACK_CLAIM_SERVICE_PREFIX}{service_center_id}"
        )
        keyboard.append([manage_button])

    keyboard.append([InlineKeyboardButton("Назад 🔙", callback_data=back_data)])

    return InlineKeyboardMarkup(keyboard)

def manage_service_centers_buttons_keyboard(service_center_id: int) -> InlineKeyboardMarkup:
    """Клавиатура с кнопками для сервисного центра"""
    back_data = f"back_to_manage_service_list_"
    logger.debug(f"Back data={back_data}")

    keyboard = [
        [InlineKeyboardButton("Отзывы 📝", callback_data=f"{CALLBACK_REVIEWS_PREFIX}{service_center_id}")],
        [InlineKeyboardButton("Прайс-лист 💰", callback_data=f"{CALLBACK_PRICES_PREFIX}{service_center_id}")],
    ]

    keyboard.append([InlineKeyboardButton("Назад 🔙", callback_data=back_data)])

    return InlineKeyboardMarkup(keyboard)


def reviews_buttons_keyboard(service_center_id: int) -> InlineKeyboardMarkup:
    """Клавиатура для отзывов"""
    keyboard = [
        [InlineKeyboardButton(
            "Назад 🔙",
            callback_data=f"{CALLBACK_CENTER_PREFIX}{service_center_id}")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def search_results_keyboard(
        service_centers: List[Dict],
        page: int,
        items_per_page: int,
        total_count: int,
        last_page: int,
        query: str,
        city_id: Optional[int] = None
) -> tuple[str, InlineKeyboardMarkup]:
    """Формирует текст сообщения и клавиатуру для результатов поиска."""
    if not service_centers:
        return "Сервисные центры не найдены.", InlineKeyboardMarkup([])

    if not query:
        message_lines = [f"<b>Лучшие сервисы в {service_centers[0]['city_name']} (страница {page + 1} из {last_page}):</b>\n"]
    else:
        message_lines = [f"Сервисы по запросу - <b>{query}</b> (страница {page + 1} из {last_page})\n"]

    # Перебираем центры с учётом пагинации
    for i, center in enumerate(service_centers, start=page * items_per_page + 1):
        avg_rating = center.get('avg_rating', 0)
        reviews_count = center.get('reviews_count', 0)
        name = center['name']
        address = center.get('address', 'Не указан')

        # Форматирование для первой страницы (page == 0)
        if page == 0 and i == 1 and not query:  # Первый элемент первой страницы
            line = (
                f"🏆 <b>{name}</b> ⭐️{avg_rating:.1f} ({reviews_count} {pluralize_reviews(reviews_count)})\n"
                f"{address}\n"
                f"/service_center_{center['id']} - подробнее\n"
                f"{'-' * 20}"
            )
        elif page == 0 and i <= 3 and not query:  # Вторые два элемента первой страницы
            line = (
                f"🔹 <b>{name}</b> ⭐️{avg_rating:.1f} ({reviews_count} {pluralize_reviews(reviews_count)})\n"
                f"{address}\n"
                f"/service_center_{center['id']} - подробнее\n"
                f"{'-' * 20}"
            )
        else:  # Все остальные элементы (включая последующие страницы)
            line = (
                f"{i}. {name} ⭐️{avg_rating:.1f} ({reviews_count} {pluralize_reviews(reviews_count)})\n"
                f"{address}\n"
                f"/service_center_{center['id']} - подробнее\n"
                f"{'-' * 20}"
            )
        message_lines.append(line)

    message_lines.append(f"\nВсего сервисных центров: {total_count}\n")
    # Добавляем дополнительное расстояние в конце
    message = "\n".join(message_lines)

    # Клавиатура пагинации
    keyboard = []
    navigation_buttons = []
    if page > 0:
        navigation_buttons.append(
            InlineKeyboardButton("⬅️ Назад", callback_data=f"search_page_{page - 1}_{query}_{city_id or ''}")
        )
    if page < last_page - 1:
        navigation_buttons.append(
            InlineKeyboardButton("Вперед ➡️", callback_data=f"search_page_{page + 1}_{query}_{city_id or ''}")
        )

    if navigation_buttons:
        keyboard.append(navigation_buttons)

    return message, InlineKeyboardMarkup(keyboard)


def service_admin_results_keyboard(
        service_centers: List[Dict],
        page: int,
        items_per_page: int,
        total_count: int,
        last_page: int,
) -> tuple[str, InlineKeyboardMarkup]:
    """Формирует текст сообщения и клавиатуру для результатов поиска."""
    if not service_centers:
        return "Сервисные центры не найдены.", InlineKeyboardMarkup([])

    message_lines = [f"<b>Ваши сервисные центры (страница {page + 1} из {last_page}):</b>"]

    # Перебираем центры с учётом пагинации
    for i, center in enumerate(service_centers, start=page * items_per_page + 1):
        avg_rating = center.get('avg_rating', 0)
        reviews_count = center.get('reviews_count', 0)
        name = center['name']
        address = center.get('address', 'Не указан')

        line = (
            f"{i}. {name} ⭐️{avg_rating:.1f} ({reviews_count} {pluralize_reviews(reviews_count)})\n"
            f"{address}\n"
            f"/manage_service_center_{center['id']} - подробнее\n"
            f"{'-' * 20}"
        )

        message_lines.append(line)

    message_lines.append(f"\nВсего сервисных центров: {total_count}\n")
    # Добавляем дополнительное расстояние в конце
    message = "\n".join(message_lines)

    # Клавиатура пагинации
    keyboard = []
    navigation_buttons = []
    if page > 0:
        navigation_buttons.append(
            InlineKeyboardButton("⬅️ Назад", callback_data=f"service_admin_page_{page - 1}")
        )
    if page < last_page - 1:
        navigation_buttons.append(
            InlineKeyboardButton("Вперед ➡️", callback_data=f"service_admin_page_{page + 1}")
        )

    if navigation_buttons:
        keyboard.append(navigation_buttons)

    return message, InlineKeyboardMarkup(keyboard)
