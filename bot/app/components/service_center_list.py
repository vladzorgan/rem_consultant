# /app/app/components/service_center_list.py
import logging

from telegram import Update
from telegram.ext import CallbackContext
from typing import Optional

from app.services import get_service_centers, search_service_centers, get_regions
from app.keyboards import service_centers_keyboard, search_results_keyboard, regions_keyboard
from app.utils.telegram_utils import send_or_edit_message, get_user_with_city

ITEMS_PER_PAGE = 5

logger = logging.getLogger(__name__)

async def service_center_list(
    update: Update,
    context: CallbackContext,
    skip: int = 0,
    limit: int = ITEMS_PER_PAGE,
    city_id: Optional[int] = None
) -> None:
    args = context.args
    user, has_city = await get_user_with_city(update)

    query = ""
    city_id = user.get('city_id') if has_city else None

    if not args:
        # Если аргументы не переданы, используем город пользователя
        if not has_city:
            keyboard = regions_keyboard(await get_regions())
            await send_or_edit_message(
                update,
                "Укажите ваш город для поиска центров по умолчанию.\nИспользование: /find_center <запрос> [rating>X] [city_id=Y]",
                reply_markup=keyboard
            )
            return
        # Query остаётся пустой строкой для поиска по городу пользователя
    else:
        # Парсинг аргументов
        for arg in args:
            if arg.startswith("city_id="):
                try:
                    city_id = int(arg[len("city_id="):])
                except ValueError:
                    await update.message.reply_text("Неверный ID города. Используйте: city_id=Y")
                    return
            else:
                query = arg

    # Запрос к API
    params = {
        "query": query,
        "city_id": city_id,
        "page": 1,
        "limit": limit
    }

    response = await search_service_centers(params)
    centers = response['data']
    total_count = response.get('total')
    last_page = response.get('last_page')

    context.user_data['search_query'] = query
    context.user_data['search_city_id'] = city_id

    message, keyboard = search_results_keyboard(
        service_centers=centers,
        page=0,
        items_per_page=ITEMS_PER_PAGE,
        total_count=total_count,
        last_page=last_page,
        query=query or "",
        city_id=city_id
    )

    await send_or_edit_message(update, message, reply_markup=keyboard, parse_mode="HTML")