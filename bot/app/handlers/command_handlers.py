import logging

from telegram import Update, User
from telegram.ext import CallbackContext, ContextTypes

from app.keyboards import main_menu_keyboard, user_settings_keyboard
from app.services import create_user, get_user

from app.services.services import notify_user, fetch_service_center, approve_service_claim, reject_service_claim, search_service_centers as search_service_centers_api

from app.keyboards.keyboards import search_results_keyboard
from app.utils.telegram_utils import get_user_with_city, send_or_edit_message

from app.helpers import format_service_center_message, format_manage_service_center_message
from app.keyboards import service_centers_buttons_keyboard, manage_service_centers_buttons_keyboard

from app.components import service_center_list

from app.services.services import get_owned_service_centers

from app.keyboards.keyboards import service_admin_results_keyboard

logger = logging.getLogger(__name__)

ADMIN_IDS = [1731471920]

async def search_centers(update: Update, context: CallbackContext) -> None:
    """Обработчик команды /find_center для поиска сервисных центров через API."""
    await service_center_list(update, context)

async def handle_center_paginate(update: Update, context: CallbackContext) -> None:
    """Обработчик пагинации поиска через API."""
    query = update.callback_query
    data = query.data.split('_')
    logger.info(data)
    page = int(data[2])
    search_query = data[3]
    city_id = int(data[4]) if data[4] else None

    params = {
        "query": search_query,
        "city_id": city_id,
        "page": page + 1,
        "limit": 5
    }

    response = await search_service_centers_api(params)
    centers = response['data']
    total_count = response.get('total')
    last_page = response.get('last_page')

    message, keyboard = search_results_keyboard(
        service_centers=centers,
        page=page,
        total_count=total_count,
        last_page=last_page,
        items_per_page=5,
        query=search_query,
        city_id=city_id
    )
    await query.edit_message_text(message, reply_markup=keyboard, parse_mode="HTML")

async def handle_center_admin_paginate(update: Update, context: CallbackContext) -> None:
    """Обработчик пагинации поиска через API."""
    query = update.callback_query
    data = query.data.split('_')
    page = int(data[3])
    logger.info(page)
    telegram_id = update.effective_user.id
    if not telegram_id:
        await send_or_edit_message(update, "Не удалось определить ваш Telegram ID.")
        return


    params = {
        "owner_id": telegram_id,
        "page": page + 1,
        "limit": 1
    }

    response = await search_service_centers_api(params)
    centers = response.get('data')
    total_count = response.get('total')
    last_page = response.get('last_page')

    message, keyboard = service_admin_results_keyboard(service_centers=centers, page=page, last_page=last_page, items_per_page=1, total_count=total_count)

    await query.edit_message_text(message, reply_markup=keyboard, parse_mode="HTML")

async def handle_center_select(update: Update, context: CallbackContext) -> None:
    """Обработчик команды /service_center_{id} для отображения детальной информации о центре."""
    text = update.message.text
    if not text.startswith("/service_center_"):
        return

    try:
        center_id = int(text[len("/service_center_"):])
    except ValueError:
        await update.message.reply_text("Неверный формат ID центра. Используйте: /service_center_{id}")
        return

    try:
        service_center = await fetch_service_center(center_id)
        telegram_id = update.effective_user.id
        is_owner = service_center.get('owner_id') == telegram_id

        if service_center:
            # Сохраняем текущую страницу перед переходом
            page = context.user_data.get('prev_center_page', 0)
            context.user_data['prev_center_page'] = page
            message_text = format_service_center_message(service_center)

            await send_or_edit_message(
                update,
                message_text,
                reply_markup=service_centers_buttons_keyboard(service_center_id=center_id, is_owner=is_owner),
                parse_mode="HTML"
            )
        else:
            await send_or_edit_message(update, "Сервисный центр не найден.")
    except Exception as e:
        await send_or_edit_message(update, "Ошибка при загрузке данных сервисного центра.")
        logger.error(f"Error in center selection: {e}")

async def handle_manage_center_select(update: Update, context: CallbackContext) -> None:
    """Обработчик команды /service_center_{id} для отображения детальной информации о центре."""
    text = update.message.text
    if not text.startswith("/manage_service_center_"):
        return

    try:
        center_id = int(text[len("/manage_service_center_"):])
    except ValueError:
        await update.message.reply_text("Неверный формат ID центра. Используйте: /manage_service_center_{id}")
        return

    try:
        service_center = await fetch_service_center(center_id)
        telegram_id = update.effective_user.id
        is_owner = service_center.get('owner_id') == telegram_id

        if service_center:
            if is_owner:
                # Сохраняем текущую страницу перед переходом
                page = context.user_data.get('prev_center_page', 0)
                context.user_data['prev_center_page'] = page
                message_text = format_manage_service_center_message(service_center)

                await send_or_edit_message(
                    update,
                    message_text,
                    reply_markup=manage_service_centers_buttons_keyboard(service_center_id=center_id),
                    parse_mode="HTML"
                )
        else:
            await send_or_edit_message(update, "Сервисный центр не найден.")
    except Exception as e:
        await send_or_edit_message(update, "Ошибка при загрузке данных сервисного центра.")
        logger.error(f"Error in center selection: {e}")

async def create_or_update_user(telegram_id: int, user_info: User) -> None:
    """Создает или обновляет пользователя с переданными данными."""
    if not user_info:
        logger.warning("No user info provided")
        return

    user_data = {
        "telegram_id": telegram_id,
        "username": user_info.username,
        "first_name": user_info.first_name or "",
        "last_name": user_info.last_name or "",
        "language_code": user_info.language_code or "en"
    }

    existing_user = await get_user(telegram_id)
    if not existing_user:
        await create_user(user_data)
        logger.info(f"Created new user: {telegram_id}")
    else:
        logger.debug(f"User {telegram_id} already exists, skipping creation")

async def handle_start(update: Update, context: CallbackContext) -> None:
    """Обработчик команды /start"""
    await create_or_update_user(update.message.from_user.id, update.message.from_user)
    await update.message.reply_text("Главное меню", reply_markup=main_menu_keyboard())

async def handle_settings(update: Update, context: CallbackContext) -> None:
    """Обработчик команды /settings"""
    await create_or_update_user(update.message.from_user.id, update.message.from_user)
    await update.message.reply_text("Настройки пользователя", reply_markup=user_settings_keyboard())

async def search_service_centers(update: Update, context: CallbackContext) -> None:
    """Обработчик поиска сервисных центров"""
    from ..components import service_center_list  # Локальный импорт для избежания циклических зависимостей
    await service_center_list(update=update, context=context)

async def handle_approve_claim(update: Update, context: CallbackContext) -> None:
    """Команда для подтверждения заявки: /approve_claim {claim_id}"""
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("У вас нет прав для этой команды.")
        return

    args = context.args
    if not args or len(args) != 1:
        await update.message.reply_text("Использование: /approve_claim {claim_id}")
        return

    try:
        claim_id = int(args[0])
        claim = await approve_service_claim(claim_id)
        if claim:
            center_name = (await fetch_service_center(claim['service_center_id']))['name']
            message = (
                f"Ваша заявка на владение сервисом <b>{center_name}</b> подтверждена!\n"
                "Теперь вы можете управлять им через меню 'Управление сервисом 🛠️'."
            )
            await notify_user(claim['telegram_id'], message, context)
            await update.message.reply_text(f"Заявка {claim_id} подтверждена.")
        else:
            await update.message.reply_text("Ошибка при подтверждении заявки.")
    except ValueError:
        await update.message.reply_text("Неверный ID заявки.")

async def handle_reject_claim(update: Update, context: ContextTypes) -> None:
    """Команда для отказа заявки: /reject_claim {claim_id}"""
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("У вас нет прав для этой команды.")
        return

    args = context.args
    if not args or len(args) != 1:
        await update.message.reply_text("Использование: /reject_claim {claim_id}")
        return

    try:
        claim_id = int(args[0])
        claim = await reject_service_claim(claim_id)
        if claim:
            center = await fetch_service_center(claim['service_center_id'])
            center_name = center['name'] if center else "Неизвестный центр"
            message = (
                f"Ваша заявка на владение сервисом <b>{center_name}</b> отменена.\n"
                "За более подробной информацией обращайтесь в поддержку - /help."
            )
            await notify_user(claim['telegram_id'], message, context)
            await update.message.reply_text(f"Заявка {claim_id} отменена.")
        else:
            await update.message.reply_text("Ошибка при отмене заявки.")
    except ValueError:
        await update.message.reply_text("Неверный ID заявки.")
    except Exception as e:
        logger.error(f"Error rejecting claim {args[0]}: {e}")
        await update.message.reply_text("Произошла ошибка при обработке команды.")