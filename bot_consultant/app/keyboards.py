from telegram import ReplyKeyboardMarkup, KeyboardButton

# Опции для клавиатуры услуг
SERVICE_OPTIONS = [
    ["Нужен ремонт / Диагностика"],
    ["Бронирование гидрогелевой плёнкой"],
    ["Стоимость кабеля/чехла/защита экрана"],
    ["Мое устройство в сервисе"],
    ["Хочу обратиться по гарантии"],
    ["Продажа/покупка телефона"],
]

# Пример ближайших сервисных центров
SERVICE_CENTERS = [
    ["M1-сервис"],
    ["Лох сервис"],
    ["Сервис Гадина"],
]

# Опции для выбора дня посещения
DATE_OPTIONS = [
    ["Сегодня"],
    ["Завтра"],
    ["Другой день"],
]

# Генерация времен с 9:00 до 20:00 с шагом 30 минут
TIME_OPTIONS = []
for hour in range(9, 20):
    TIME_OPTIONS.append([f"{hour}:00 - {hour}:30"])
    TIME_OPTIONS.append([f"{hour}:30 - {hour + 1}:00"])
TIME_OPTIONS.append(["20:00"])

# Клавиатура для запроса номера телефона
PHONE_KEYBOARD = ReplyKeyboardMarkup(
    [[KeyboardButton("Поделиться номером", request_contact=True)]],
    one_time_keyboard=True,
    resize_keyboard=True
)