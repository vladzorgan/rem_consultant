# /app/utils/telegram_utils.py
import logging

from telegram import Update
from typing import Optional, Tuple

from app.services import get_user

logger = logging.getLogger(__name__)

async def send_or_edit_message(
        update: Update,
        text: str,
        reply_markup=None,
        parse_mode: Optional[str] = None
) -> None:
    """
    Отправляет новое сообщение или редактирует существующее в зависимости от контекста.

    Args:
        update: Объект Update от Telegram
        text: Текст сообщения
        reply_markup: Клавиатура (опционально)
        parse_mode: Режим парсинга текста (например, 'HTML')
    """

    try:
        query = update.callback_query if hasattr(update, 'callback_query') else None
        if query:
            await query.edit_message_text(text, reply_markup=reply_markup, parse_mode=parse_mode)
        else:
            await update.message.reply_text(text, reply_markup=reply_markup, parse_mode=parse_mode)
    except Exception as e:
        logger.error(f"Failed to send/edit message: {e}")
        raise

async def get_user_with_city(update: Update) -> Tuple[Optional[dict], bool]:
    """Получает пользователя и проверяет наличие города."""
    user = await get_user(update.callback_query.from_user.id if update.callback_query else update.message.from_user.id)
    has_city = user and user.get('city_id') is not None
    return user, has_city