from telegram import Update
from telegram.ext import CallbackContext

from app.services import fetch_cities
from app.keyboards import cities_keyboard
from app.utils.telegram_utils import send_or_edit_message


async def city_list(update: Update, context: CallbackContext) -> None:
    """Отображает список городов для выбранного региона"""
    query = update.callback_query if hasattr(update, 'callback_query') else None
    callback_data = query.data if query else None

    if not callback_data or "_" not in callback_data:
        await send_or_edit_message(update, "Ошибка: некорректные данные региона.")
        return

    try:
        region_id = int(callback_data.split("_")[1])
        cities = await fetch_cities(region_id)
        text = "Города не найдены." if not cities else "Выберите город:"
        keyboard = cities_keyboard(cities)

        await send_or_edit_message(update, text, reply_markup=keyboard)

    except ValueError:
        await send_or_edit_message(update, "Ошибка: некорректный ID региона.")
    except Exception as e:
        await send_or_edit_message(update, "Произошла ошибка при загрузке городов.")
        print(f"Error in city_list: {e}")