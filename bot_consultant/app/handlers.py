import logging
import re

import httpx
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, JobQueue

from services import fetch_cities
from config import CITY, SERVICE, REPAIR_DETAILS, CHOOSE_SERVICE_CENTER, CHOOSE_DATE, CHOOSE_TIME, ENTER_NAME, \
    ENTER_PHONE, DEVICE_IN_SERVICE, ORDER_REGEX, PHONE_REGEX, NAME_REGEX
from keyboards import SERVICE_OPTIONS, SERVICE_CENTERS, DATE_OPTIONS, TIME_OPTIONS, PHONE_KEYBOARD
from utils import normalize_phone

logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Начало диалога: приветствие и запрос города"""
    user = update.message.from_user.first_name
    user_id = update.message.from_user.id
    chat_id = update.message.chat_id
    logger.info(f"Пользователь {user} (ID: {user_id}) начал диалог")
    welcome_message = (
        "Для того, чтобы мы могли Вас проконсультировать, напишите Ваш город. "
        "Только название! Пример: Санкт-Петербург, Ростов-на-Дону, Уфа"
    )
    # Очищаем все данные перед началом нового диалога
    context.user_data.clear()
    context.chat_data.clear()
    await update.message.reply_text(welcome_message)

    return CITY


async def get_city(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Сохранение города и отображение клавиатуры с услугами"""
    city_name = update.message.text
    user_id = update.message.from_user.id
    logger.info(f"Пользователь (ID: {user_id}) ввел город: {city_name}")

    try:
        cities = await fetch_cities({"name": city_name, "limit": 1300})

        # Ищем полное совпадение по имени города
        matched_city = next(
            (city for city in cities if city["name"].lower() == city_name.lower()),
            None
        )

        if matched_city:
            # Сохраняем данные о городе в context.user_data
            context.user_data['city'] = matched_city
            logger.info(f"Город найден: {matched_city['name']} (ID: {matched_city['id']})")

            # Создаём клавиатуру с услугами
            reply_keyboard = ReplyKeyboardMarkup(
                SERVICE_OPTIONS,
                one_time_keyboard=True,
                resize_keyboard=True
            )

            await update.message.reply_text(
                f"Отлично, вы выбрали город: {matched_city['name']}. Что вам нужно?",
                reply_markup=reply_keyboard
            )
            return SERVICE  # Переход к следующему состоянию
        else:
            # Полного совпадения нет, ищем частичные совпадения
            suggestions = [
                city["name"] for city in cities
                if city_name.lower() in city["name"].lower()
            ]

            if suggestions:
                # Предлагаем варианты автодополнения
                suggestion_keyboard = ReplyKeyboardMarkup(
                    [[suggestion] for suggestion in suggestions[:5]],  # Ограничиваем до 5 вариантов
                    one_time_keyboard=True,
                    resize_keyboard=True
                )
                await update.message.reply_text(
                    f"Город '{city_name}' не найден. Возможно, вы имели в виду один из этих городов?\n"
                    "Выберите вариант или введите город заново:",
                    reply_markup=suggestion_keyboard
                )
                context.user_data['suggested_cities'] = cities  # Сохраняем города для следующего шага
                return CITY  # Остаёмся в состоянии CITY
            else:
                # Нет даже частичных совпадений
                await update.message.reply_text(
                    "Город не найден. Пожалуйста, укажите существующий город. Например: Санкт-Петербург, Ростов-на-Дону, Уфа"
                )
                return CITY

    except httpx.HTTPStatusError as e:
        logger.error(f"Ошибка HTTP при запросе к API: {e}")
        await update.message.reply_text(
            "Произошла ошибка при проверке города. Попробуйте снова или обратитесь в поддержку."
        )
        return CITY
    except httpx.RequestError as e:
        logger.error(f"Ошибка сети при запросе к API: {e}")
        await update.message.reply_text(
            "Не удалось подключиться к серверу. Попробуйте позже."
        )
        return CITY
    except Exception as e:
        logger.error(f"Неизвестная ошибка: {e}")
        await update.message.reply_text(
            "Что-то пошло не так. Попробуйте снова."
        )
        return CITY


async def get_service(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработка выбранной услуги"""
    service = update.message.text
    user_id = update.message.from_user.id
    chat_id = update.message.chat_id
    logger.info(f"Пользователь (ID: {user_id}) выбрал услугу: {service}")
    context.user_data['service'] = service
    city = context.user_data['city']

    if service == "Нужен ремонт / Диагностика":
        await update.message.reply_text(
            "Какая у Вас модель? Что с устройством?\n"
            "Например: iPhone 12 Pro Max, быстро разряжается"
        )
        
        return REPAIR_DETAILS
    elif service == "Бронирование гидрогелевой плёнкой":
        await update.message.reply_text(
            f"🔥 Бронирование гидрогелевой пленкой.\n"
            f"Она плотно ложится на поверхность и стягивает деффекты (царапины).\n\n"
            f"+ дополнительная защита устройства.\n"
            f"+ срок службы в 4-5 раз дольше любого стекла\n"
            f"+ защита от влаги\n\n"
            f"🔥 Одна сторона Устройства – от 990 руб\n\n"
            f"Пленка вырезается плоттером под Ваше устройство, точную стоимость сможем озвучить в сервисном центре\n\n"
            f"В городе {city} несколько сервисов:"
        )
        logger.info(f"Пользователь (ID: {user_id}) завершил диалог с услугой: {service}")
        return ConversationHandler.END
    elif service == "Стоимость кабеля/чехла/защита экрана":
        await update.message.reply_text(
            f"Стоимость кабеля/чехла/защита экрана\n"
            f"✅ Защита экрана:\n\n"
            f"Защитное стекло\n"
            f"- на телефон от 390 руб.\n"
            f"- iPad от 990 руб.\n\n"
            f"✅ Кабели от 590 руб.\n"
            f"✅ Чехлы от 390 руб.\n\n"
            f"В городе {city} несколько сервисов:\n\n"
            f"Приходите, будем ждать Вас! 🙂"
        )
        logger.info(f"Пользователь (ID: {user_id}) завершил диалог с услугой: {service}")
        return ConversationHandler.END
    elif service == "Мое устройство в сервисе":
        await update.message.reply_text(
            f"Моё устройство в сервисе\n"
            f"Напишите номер заказа в формате XXX-XXXXX или контактный номер телефона указанный в заказе в формате 79999999999\n\n"
            f"Например: 253-59912 или 79217578234"
        )
        return DEVICE_IN_SERVICE
    elif service == "Хочу обратиться по гарантии":
        await update.message.reply_text(
            f"Гарантия\n"
            f"Если у вас имеются вопросы по качеству обслуживания или качеству установленных запчастей, "
            f"просим Вас обратиться в сервисный центр, в котором был произведен ремонт. "
            f"Желательно при себе иметь документы, которые выдали Вам после ремонта."
        )
        logger.info(f"Пользователь (ID: {user_id}) завершил диалог с услугой: {service}")
        return ConversationHandler.END
    elif service == "Продажа/покупка телефона":
        await update.message.reply_text(
            f"Выкуп телефонов\n"
            f"По данным вопросам Вас смогут проконсультировать наши коллеги в Pedant.Market. Вы можете написать или позвонить:\n\n"
            f"Telegram: https://t.me/Pedant_Market_bot?start=pm_start-selltg\n\n"
            f"WhatsApp: https://wa.me/79279260969\n\n"
            f"Горячая линия: 8 (800) 301-33-09"
        )
        logger.info(f"Пользователь (ID: {user_id}) завершил диалог с услугой: {service}")
        return ConversationHandler.END
    else:
        logger.warning(f"Пользователь (ID: {user_id}) выбрал неизвестную услугу: {service}")
        await update.message.reply_text("Что-то пошло не так. Пожалуйста, выберите услугу из предложенных.")
        return SERVICE


async def device_in_service(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработка ввода номера заказа или телефона для 'Мое устройство в сервисе'"""
    user_input = update.message.text
    user_id = update.message.from_user.id
    chat_id = update.message.chat_id
    city = context.user_data['city']
    service = context.user_data['service']
    logger.info(f"Пользователь (ID: {user_id}) ввел для 'Мое устройство в сервисе': {user_input}")

    if re.match(ORDER_REGEX, user_input):
        context.user_data['order_or_phone'] = user_input
        await update.message.reply_text(
            f"Вы выбрали:\n"
            f"Город: {city}\n"
            f"Услуга: {service}\n"
            f"Номер заказа: {user_input}\n"
            "Мы проверим статус вашего устройства и свяжемся с вами!"
        )
        logger.info(
            f"Пользователь (ID: {user_id}) завершил диалог с услугой: {service}, ввел номер заказа: {user_input}")
        return ConversationHandler.END
    elif normalize_phone(user_input):
        phone = normalize_phone(user_input)
        context.user_data['order_or_phone'] = phone
        await update.message.reply_text(
            f"Вы выбрали:\n"
            f"Город: {city}\n"
            f"Услуга: {service}\n"
            f"Контактный номер телефона: {phone}\n"
            "Мы проверим статус вашего устройства и свяжемся с вами!"
        )
        logger.info(f"Пользователь (ID: {user_id}) завершил диалог с услугой: {service}, ввел телефон: {phone}")
        return ConversationHandler.END
    else:
        logger.warning(
            f"Пользователь (ID: {user_id}) ввел некорректные данные для 'Мое устройство в сервисе': {user_input}")
        await update.message.reply_text(
            "Некорректный формат. Пожалуйста, введите номер заказа в формате XXX-XXXXX (например, 253-59912) "
            "или контактный номер телефона в формате 79999999999 (например, 79217578234)."
        )
        return DEVICE_IN_SERVICE


async def get_repair_details(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработка модели и проблемы, вывод предложений и выбор сервиса"""
    repair_details = update.message.text
    user_id = update.message.from_user.id
    chat_id = update.message.chat_id
    logger.info(f"Пользователь (ID: {user_id}) ввел детали ремонта: {repair_details}")
    city = context.user_data['city']
    service = context.user_data['service']

    try:
        model, issue = [part.strip() for part in repair_details.split(',', 1)]
        context.user_data['model'] = model
        context.user_data['issue'] = issue
        logger.info(f"Пользователь (ID: {user_id}) указал модель: {model}, проблема: {issue}")
    except ValueError:
        logger.warning(f"Пользователь (ID: {user_id}) ввел некорректные детали ремонта: {repair_details}")
        await update.message.reply_text(
            "Пожалуйста, укажите модель и проблему через запятую, например: iPhone 12 Pro Max, быстро разряжается"
        )
        
        return REPAIR_DETAILS

    await update.message.reply_text(
        "🔥 Стоимость по акции 👉 5490 руб."
    )
    await update.message.reply_text(
        f"Нажмите на нужную кнопку, чтобы выбрать сервис в городе {city}👇",
        reply_markup=SERVICE_CENTERS
    )
    return CHOOSE_SERVICE_CENTER


async def choose_service_center(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Выбор сервисного центра и запрос даты посещения"""
    service_center = update.message.text
    user_id = update.message.from_user.id
    chat_id = update.message.chat_id
    logger.info(f"Пользователь (ID: {user_id}) выбрал сервисный центр: {service_center}")
    context.user_data['service_center'] = service_center

    await update.message.reply_text(
        f"Вы выбрали сервис: {service_center}. Когда планируете посетить?",
        reply_markup=DATE_OPTIONS
    )
    return CHOOSE_DATE


async def choose_date(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Выбор даты и запрос времени посещения"""
    visit_date = update.message.text
    user_id = update.message.from_user.id
    chat_id = update.message.chat_id
    logger.info(f"Пользователь (ID: {user_id}) выбрал день посещения: {visit_date}")
    context.user_data['visit_date'] = visit_date

    await update.message.reply_text(
        f"Вы выбрали день: {visit_date}. В какое время вам удобно?",
        reply_markup=TIME_OPTIONS
    )
    return CHOOSE_TIME


async def choose_time(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Выбор времени и запрос имени"""
    visit_time = update.message.text
    user_id = update.message.from_user.id
    chat_id = update.message.chat_id
    logger.info(f"Пользователь (ID: {user_id}) выбрал время посещения: {visit_time}")
    context.user_data['visit_time'] = visit_time

    await update.message.reply_text(
        "Пожалуйста, укажите ваше имя для записи (минимум 2 буквы, только буквы и пробелы)."
    )
    return ENTER_NAME


async def enter_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Ввод имени и запрос номера телефона с валидацией"""
    name = update.message.text
    user_id = update.message.from_user.id
    chat_id = update.message.chat_id
    logger.info(f"Пользователь (ID: {user_id}) ввел имя: {name}")

    if len(name) < 2 or not re.match(NAME_REGEX, name):
        logger.warning(f"Пользователь (ID: {user_id}) ввел некорректное имя: {name}")
        await update.message.reply_text(
            "Некорректное имя. Пожалуйста, введите имя длиной минимум 2 буквы, используя только буквы и пробелы (например, Анна, Иван Петров)."
        )
        return ENTER_NAME

    context.user_data['name'] = name
    await update.message.reply_text(
        "Введите Ваш номер телефона в формате 79999999999 или нажмите на кнопку Поделиться номером 👇",
        reply_markup=PHONE_KEYBOARD
    )
    return ENTER_PHONE


async def enter_phone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Подтверждение с номером телефона и завершение диалога"""
    phone = None
    user_id = update.message.from_user.id
    chat_id = update.message.chat_id

    if update.message.contact:
        phone_raw = update.message.contact.phone_number
        phone = normalize_phone(phone_raw)
        logger.info(f"Пользователь (ID: {user_id}) поделился контактом: {phone_raw}, нормализованный: {phone}")
        if not phone:
            logger.warning(f"Пользователь (ID: {user_id}) ввел некорректный контакт: {phone_raw}")
            await update.message.reply_text(
                "Номер телефона из контакта некорректен. Пожалуйста, введите номер вручную "
                "(например, +79991234567, 8 (999) 123-45-67, 79991234567).",
                reply_markup=PHONE_KEYBOARD
            )
            return ENTER_PHONE
    elif update.message.text:
        phone_raw = update.message.text
        phone = normalize_phone(phone_raw)
        logger.info(f"Пользователь (ID: {user_id}) ввел номер вручную: {phone_raw}, нормализованный: {phone}")
        if not phone:
            logger.warning(f"Пользователь (ID: {user_id}) ввел некорректный номер: {phone_raw}")
            await update.message.reply_text(
                "Некорректный номер телефона. Пожалуйста, введите номер в любом формате "
                "(например, +79991234567, 8 (999) 123-45-67, 79991234567).",
                reply_markup=PHONE_KEYBOARD
            )
            return ENTER_PHONE
    else:
        logger.warning(f"Пользователь (ID: {user_id}) отправил некорректный ввод вместо номера")
        await update.message.reply_text(
            "Пожалуйста, поделитесь номером через кнопку или введите его вручную "
            "(например, +79991234567, 8 (999) 123-45-67, 79991234567).",
            reply_markup=PHONE_KEYBOARD
        )
        return ENTER_PHONE

    city = context.user_data['city']
    service = context.user_data['service']
    model = context.user_data.get('model', 'Не указано')
    issue = context.user_data.get('issue', 'Не указано')
    service_center = context.user_data['service_center']
    visit_date = context.user_data['visit_date']
    visit_time = context.user_data['visit_time']
    name = context.user_data['name']

    context.user_data['phone'] = phone
    logger.info(f"Пользователь (ID: {user_id}) успешно завершил диалог с данными: {context.user_data}")

    await update.message.reply_text(
        f"Вы выбрали:\n"
        f"Город: {city}\n"
        f"Услуга: {service}\n"
        f"Модель: {model}\n"
        f"Проблема: {issue}\n"
        f"Сервисный центр: {service_center}\n"
        f"День посещения: {visit_date}\n"
        f"Время посещения: {visit_time}\n"
        f"Имя: {name}\n"
        f"Номер телефона: {phone}\n"
        "Спасибо! Скоро с вами свяжутся для подтверждения."
    )
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Отмена диалога"""
    user_id = update.message.from_user.id
    logger.info(f"Пользователь (ID: {user_id}) отменил диалог")
    await update.message.reply_text("Диалог отменен. Чтобы начать заново, используйте /start.")
    return ConversationHandler.END