import sys
import os

from app.handlers.callback_handlers import back_to_list_handler

# Добавляем корневую директорию проекта в sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters

from app.handlers import (
    handle_start, handle_settings, search_centers,
    handle_region_select, handle_city_select, handle_back, handle_reviews,
    setup_conversations, handle_center_paginate, handle_center_select,
    handle_approve_claim, handle_reject_claim, handle_message,
    service_center_selection_handler, handle_center_admin_paginate,
    handle_manage_center_select
)

# Добавляем корневую директорию проекта в sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.config import TELEGRAM_BOT_TOKEN

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[logging.StreamHandler(), logging.FileHandler("bot.log")]
)
logger = logging.getLogger(__name__)

def setup_handlers(application) -> None:
    """Register all bot handlers."""
    # Команды
    application.add_handler(CommandHandler("start", handle_start))
    application.add_handler(CommandHandler("settings", handle_settings))
    application.add_handler(CommandHandler("service_centers", search_centers))
    application.add_handler(CommandHandler("approve_claim", handle_approve_claim))
    application.add_handler(CommandHandler("reject_claim", handle_reject_claim))

    # Кнопки
    application.add_handler(CallbackQueryHandler(handle_region_select, pattern="^region_"))
    application.add_handler(CallbackQueryHandler(handle_city_select, pattern="^city_"))
    application.add_handler(CallbackQueryHandler(handle_reviews, pattern="^reviews_"))
    application.add_handler(CallbackQueryHandler(service_center_selection_handler, pattern="^center_"))
    application.add_handler(CallbackQueryHandler(handle_center_paginate, pattern="^search_page_"))
    application.add_handler(CallbackQueryHandler(handle_center_admin_paginate, pattern="^service_admin_page_"))
    # application.add_handler(CallbackQueryHandler(handle_back, pattern="^back"))
    application.add_handler(CallbackQueryHandler(back_to_list_handler, pattern="^back_to_list_"))

    # ConversationHandler
    setup_conversations(application)

    # Общие сообщения
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(MessageHandler(filters.Regex(r'^/service_center_\d+$'), handle_center_select))
    application.add_handler(MessageHandler(filters.Regex(r'^/manage_service_center_\d+$'), handle_manage_center_select))

def main() -> None:
    """Start the bot."""
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    try:
        setup_handlers(application)
        logger.info("Starting bot...")
        application.run_polling(allowed_updates=Update.ALL_TYPES)
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Bot stopped by user.")
        application.stop()

if __name__ == "__main__":
    main()