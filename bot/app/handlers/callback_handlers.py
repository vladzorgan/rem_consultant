import logging

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext, ConversationHandler, CallbackQueryHandler, MessageHandler, filters
from app.keyboards import service_centers_keyboard, service_centers_buttons_keyboard, reviews_buttons_keyboard
from app.services import get_user, get_service_centers, fetch_service_center, fetch_reviews, update_user_city, create_service_claim_request
from app.helpers import format_service_center_message
from app.components import service_center_list, region_list, city_list
from app.utils.telegram_utils import send_or_edit_message, get_user_with_city

from app.keyboards import search_results_keyboard
from app.services import search_service_centers

logger = logging.getLogger(__name__)

ITEMS_PER_PAGE = 5
CALLBACK_CENTER_PREFIX = "center_"
CALLBACK_CLAIM_SERVICE_PREFIX = "claim_service_"
CALLBACK_CENTER_PAGE_PREFIX = "center_page_"
CALLBACK_REVIEWS_PREFIX = "reviews_"

ASK_CONTACT, ASK_MESSAGE = range(2)

async def handle_region_select(update: Update, context: CallbackContext) -> None:
    """Обработчик выбора региона"""
    await city_list(update=update, context=context)

async def handle_city_select(update: Update, context: CallbackContext) -> None:
    """Обработчик выбора города"""
    query = update.callback_query
    try:
        city_id = int(query.data.split("_")[1])
        await update_user_city(query.from_user.id, city_id)
        await service_center_list(update, context=context, city_id=city_id)
    except (ValueError, IndexError) as e:
        await send_or_edit_message(update, "Ошибка: некорректный ID города.")
        logger.error(f"Invalid city callback data: {query.data} - {e}")

async def back_to_list_handler(update: Update, context: CallbackContext) -> None:
    """Обработчик кнопки 'Назад' для возврата к списку центров."""
    query = update.callback_query
    callback_data = query.data
    logger.debug(f"Received callback: {callback_data}")

    if not callback_data.startswith("back_to_list_"):
        return

    page = context.user_data.get("prev_center_page", 0)
    search_query = context.user_data.get("search_query", "")
    city_id = context.user_data.get("search_city_id", None)

    # Запрос к API
    params = {
        "query": search_query,
        "city_id": city_id,
        "skip": page * 5,
        "limit": 5
    }

    response = await search_service_centers(params)
    centers = response['data']
    total_count = response.get('total')
    last_page = response.get('last_page')

    message, keyboard = search_results_keyboard(
        service_centers=centers,
        page=page,
        items_per_page=5,
        total_count=total_count,
        last_page=last_page,
        query=search_query,
        city_id=city_id
    )

    await query.edit_message_text(message, reply_markup=keyboard, parse_mode="HTML")
    logger.debug(f"Returned to service centers list: page={page}, query={search_query}, city_id={city_id}")

async def handle_back(update: Update, context: CallbackContext) -> None:
    """Обработчик кнопки 'назад'"""
    query = update.callback_query
    callback_data = query.data

    if callback_data.startswith("back_center_list"):
        user, has_city = await get_user_with_city(update)
        if not has_city:
            await send_or_edit_message(update, "Не удалось определить ваш город.")
            return

        # Получаем сохранённую страницу, по умолчанию 0 (первая страница)
        page = context.user_data.get('prev_center_page', 0)
        skip = page * ITEMS_PER_PAGE

        await service_center_list(
            update=update,
            context=context,
            skip=skip,
            limit=ITEMS_PER_PAGE,
            city_id=user['city_id']
        )
    elif callback_data.startswith("back_region_list"):
        await region_list(update)

async def service_center_selection_handler(update: Update, context: CallbackContext) -> None:
    """Обработчик выбора конкретного сервисного центра"""
    query = update.callback_query
    callback_data = query.data

    # Проверяем, что это выбор центра, а не пагинация
    if not callback_data.startswith(CALLBACK_CENTER_PREFIX) or callback_data.startswith(CALLBACK_CENTER_PAGE_PREFIX):
        return

    try:
        center_id = int(callback_data[len(CALLBACK_CENTER_PREFIX):])
        service_center = await fetch_service_center(center_id)
        if service_center:
            # Сохраняем текущую страницу перед переходом
            page = context.user_data.get('prev_center_page', 0)
            context.user_data['prev_center_page'] = page
            message_text = format_service_center_message(service_center)

            await send_or_edit_message(
                update,
                message_text,
                reply_markup=service_centers_buttons_keyboard(center_id),
                parse_mode="HTML"
            )
        else:
            await send_or_edit_message(update, "Сервисный центр не найден.")
    except ValueError:
        await send_or_edit_message(update, "Ошибка: некорректный ID сервисного центра.")
        logger.error(f"Invalid center ID in callback: {callback_data}")
    except Exception as e:
        await send_or_edit_message(update, "Ошибка при загрузке данных сервисного центра.")
        logger.error(f"Error in center selection: {e}")

async def service_center_pagination_handler(update: Update, context: CallbackContext) -> None:
    """Обработчик пагинации списка сервисных центров"""
    query = update.callback_query
    callback_data = query.data

    if not callback_data.startswith(CALLBACK_CENTER_PAGE_PREFIX):
        return

    try:
        page = int(callback_data[len(CALLBACK_CENTER_PAGE_PREFIX):])
        user, has_city = await get_user_with_city(update)
        if not has_city:
            await send_or_edit_message(update, "Не удалось определить ваш город.")
            return

        context.user_data['prev_center_page'] = page
        await service_center_list(
            update=update,
            context=context,
            skip=page * ITEMS_PER_PAGE,
            limit=ITEMS_PER_PAGE,
            city_id=user['city_id']
        )
    except ValueError:
        await send_or_edit_message(update, "Ошибка: некорректный номер страницы.")
        logger.error(f"Invalid page number in callback: {callback_data}")
    except Exception as e:
        await send_or_edit_message(update, "Ошибка при загрузке списка сервисных центров.")
        logger.error(f"Error in pagination: {e}")

async def claim_service_handler(update: Update, context: CallbackContext) -> int:
    """Обработчик кнопки 'Это мой сервис'"""
    query = update.callback_query
    callback_data = query.data
    logger.debug(f"Claim service handler triggered: {callback_data}")

    center_id = int(callback_data[len(CALLBACK_CLAIM_SERVICE_PREFIX):])
    user, has_city = await get_user_with_city(update)

    if not user:
        await query.answer("Ошибка: пользователь не найден.", show_alert=True)
        return ConversationHandler.END

    telegram_id = user['telegram_id']
    center = await fetch_service_center(center_id)

    if not center:
        await query.answer("Сервисный центр не найден.", show_alert=True)
        return ConversationHandler.END

    if center.get('owner_id') is not None:
        await query.answer("Этот сервис уже привязан к другому пользователю.", show_alert=True)
        return ConversationHandler.END

    context.user_data['claim_center_id'] = center_id
    context.user_data['telegram_id'] = telegram_id

    await query.edit_message_text(
        "Пожалуйста, укажите контакт для связи (например, телефон):",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Отмена", callback_data='cancel_claim_service')]]),
    )
    logger.debug(f"Entering ASK_CONTACT state for center_id={center_id}")
    return ASK_CONTACT

async def ask_contact_handler(update: Update, context: CallbackContext) -> int:
    """Обработчик ввода контакта"""
    contact = update.message.text.strip()
    logger.debug(f"Received contact: '{contact}' from chat_id={update.message.chat_id}")

    if not contact:
        await update.message.reply_text("Контакт не может быть пустым. Попробуйте ещё раз:")
        return ASK_CONTACT

    context.user_data['claim_contact'] = contact

    await update.message.reply_text(
        "Укажите сообщение для заявки:",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Отмена", callback_data='cancel_claim_service')]]),
    )
    logger.debug("Entering ASK_MESSAGE state")
    return ASK_MESSAGE

async def ask_handle_message(update: Update, context: CallbackContext) -> int:
    """Обработчик ввода сообщения и создание заявки"""
    message = update.message.text.strip()
    logger.debug(f"Received message: '{message}'")

    if not message:
        await update.message.reply_text("Сообщение не может быть пустым. Попробуйте ещё раз:")
        return ASK_MESSAGE

    center_id = context.user_data.get('claim_center_id')
    telegram_id = context.user_data.get('telegram_id')
    contact = context.user_data.get('claim_contact')

    center = await fetch_service_center(center_id)
    if not center:
        await update.message.reply_text("Сервисный центр не найден.")
        return ConversationHandler.END

    success = await create_service_claim_request({
        "service_center_id": center_id,
        "telegram_id": telegram_id,
        "message": message,
        "contact": contact
    })

    if success:
        await update.message.reply_text(
            f"Заявка на владение сервисом '{center['name']}' отправлена!\nКонтакт: {contact}\nСообщение: {message}")
    else:
        await update.message.reply_text("Ошибка при создании заявки.")

    context.user_data.clear()
    return ConversationHandler.END

async def cancel_handler(update: Update, context: CallbackContext) -> int:
    """Обработчик отмены"""
    query = update.callback_query
    center_id = context.user_data.get('claim_center_id', 0)
    await query.edit_message_text(
        "Действие отменено."
    )
    context.user_data.clear()
    return ConversationHandler.END

def setup_conversations(application):
    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(claim_service_handler, pattern=f"^{CALLBACK_CLAIM_SERVICE_PREFIX}")],
        states={
            ASK_CONTACT: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_contact_handler)],
            ASK_MESSAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_handle_message)]
        },
        fallbacks=[CallbackQueryHandler(cancel_handler, pattern="cancel_claim_service")],
    )
    application.add_handler(conv_handler)

async def handle_reviews(update: Update, context: CallbackContext) -> None:
    """Обработчик просмотра отзывов"""
    query = update.callback_query
    callback_data = query.data

    if not callback_data.startswith(CALLBACK_REVIEWS_PREFIX):
        return

    try:
        center_id = int(callback_data[len(CALLBACK_REVIEWS_PREFIX):])
        service_center = await fetch_service_center(center_id)
        if not service_center:
            await send_or_edit_message(update, "Сервисный центр не найден.")
            return

        reviews = await fetch_reviews(service_center_id=center_id, skip=0, limit=5)
        reviews_text = f"Отзывы о сервисном центре: <b>{service_center['name']}</b>\n\n"
        for review in reviews:
            reviews_text += f"{'⭐' * int(review['rating'])}\n\n"
            reviews_text += f"<b>{review['author']}</b>: {review['text']}\n\n{'─' * 10}\n"

        await send_or_edit_message(
            update,
            reviews_text.rstrip(),
            reply_markup=reviews_buttons_keyboard(center_id),
            parse_mode='HTML'
        )
    except (ValueError, IndexError) as e:
        await send_or_edit_message(update, "Ошибка: некорректные данные отзывов.")
        logger.error(f"Invalid reviews callback data: {callback_data} - {e}")