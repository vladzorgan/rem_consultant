from telegram import Update

from app.services import get_regions
from app.keyboards import regions_keyboard
from app.utils.telegram_utils import send_or_edit_message


async def show_region_list(update: Update) -> None:
    """Отображает список регионов"""
    try:
        regions = await get_regions()
        text = "Регионы не найдены." if not regions else "Выберите регион:"
        keyboard = regions_keyboard(regions)

        await send_or_edit_message(update, text, reply_markup=keyboard)

    except Exception as e:
        await send_or_edit_message(update, "Произошла ошибка при загрузке регионов.")
        print(f"Error in region_list: {e}")