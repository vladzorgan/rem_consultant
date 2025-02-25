import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler, ContextTypes
from handlers import start, get_city, get_service, get_repair_details, choose_service_center, choose_date, choose_time, \
    enter_name, enter_phone, device_in_service, cancel
from config import TOKEN, CITY, SERVICE, REPAIR_DETAILS, CHOOSE_SERVICE_CENTER, CHOOSE_DATE, CHOOSE_TIME, ENTER_NAME, \
    ENTER_PHONE, DEVICE_IN_SERVICE

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def main() -> None:
    """Запуск бота"""
    application = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", lambda update, context: start(update, context))],
        states={
            CITY: [MessageHandler(filters.TEXT & ~filters.COMMAND,
                                  lambda update, context: get_city(update, context))],
            SERVICE: [MessageHandler(filters.TEXT & ~filters.COMMAND,
                                     lambda update, context: get_service(update, context))],
            REPAIR_DETAILS: [MessageHandler(filters.TEXT & ~filters.COMMAND,
                                            lambda update, context: get_repair_details(update, context))],
            CHOOSE_SERVICE_CENTER: [MessageHandler(filters.TEXT & ~filters.COMMAND,
                                                   lambda update, context: choose_service_center(update, context,
                                                                                                ))],
            CHOOSE_DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND,
                                         lambda update, context: choose_date(update, context))],
            CHOOSE_TIME: [MessageHandler(filters.TEXT & ~filters.COMMAND,
                                         lambda update, context: choose_time(update, context))],
            ENTER_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND,
                                        lambda update, context: enter_name(update, context))],
            ENTER_PHONE: [MessageHandler(filters.ALL & ~filters.COMMAND,
                                         lambda update, context: enter_phone(update, context))],
            DEVICE_IN_SERVICE: [MessageHandler(filters.TEXT & ~filters.COMMAND,
                                               lambda update, context: device_in_service(update, context))],
        },
        fallbacks=[
            CommandHandler("start", lambda update, context: start(update, context)),
            CommandHandler("cancel", cancel)
        ],
    )

    # Обработчик ошибок
    async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        logger.error(f"Произошла ошибка: {context.error}", exc_info=True)
        if update:
            await update.message.reply_text("Произошла ошибка. Попробуйте снова или свяжитесь с поддержкой.")

    application.add_handler(conv_handler)
    application.add_error_handler(error_handler)

    logger.info("Бот запущен!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()