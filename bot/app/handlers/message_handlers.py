from telegram import Update
from telegram.ext import ContextTypes  # Используем ContextTypes вместо CallbackContext
import logging

from app.services import get_user, get_service_centers, get_regions, search_service_centers
from app.handlers import handle_settings, handle_start
from app.utils.telegram_utils import send_or_edit_message, get_user_with_city

from app.components import service_center_list

from app.keyboards.keyboards import service_admin_results_keyboard

logger = logging.getLogger(__name__)

async def handle_message(update: Update, context: ContextTypes) -> None:
    """Process incoming text messages from users."""
    text = update.message.text
    user, has_city = await get_user_with_city(update)

    if text == 'Сервисные центры 🛠️':
        await handle_service_centers(update, context)
    elif text == 'Настройки пользователя ⚙️':
        await handle_settings(update, context)
    elif text == 'Управление сервисом 🛠️':
        await handle_service_management(update, context, user, has_city)
    elif text == 'Назад 🔙':
        await handle_start(update, context)
    else:
        logger.debug(f"Unhandled message: {text}")

async def handle_service_centers(update: Update, context: ContextTypes) -> None:
    await service_center_list(update, context)

async def handle_repair_price(update: Update, context: ContextTypes) -> None:
    """Handle request to calculate repair price."""
    await send_or_edit_message(update, "Выберите модель для расчета стоимости...")

async def handle_service_management(update: Update, context: ContextTypes, user: dict, has_city: bool) -> None:
    """Handle service management options for admins."""
    if not has_city:
        await send_or_edit_message(update, "Сначала укажите город в настройках!")
        return

    telegram_id = user.get('telegram_id')
    city_id = user.get('city_id')
    if not telegram_id:
        await send_or_edit_message(update, "Не удалось определить ваш Telegram ID.")
        return

    try:
        # Запрос к API для получения центров, где пользователь — владелец
        params = {
            "owner_id": telegram_id,
            "city_id": city_id,
            "query": "",
            "page": 1,
            "limit": 1
        }

        response = await search_service_centers(params)

        centers = response.get('data')
        total_count = response.get('total')
        last_page = response.get('last_page')

        if not centers:
            await send_or_edit_message(update, "У вас пока нет сервисных центров.")
            return

        message, keyboard = service_admin_results_keyboard(
            service_centers=centers,
            page=0,
            total_count=total_count,
            last_page=last_page,
            items_per_page=5,
        )

        await send_or_edit_message(
            update,
            message,
            reply_markup=keyboard,
            parse_mode="HTML"
        )

    except Exception as e:
        logger.error(f"Error fetching managed centers: {e}")
        await send_or_edit_message(update, "Ошибка при загрузке данных. Попробуйте позже.")