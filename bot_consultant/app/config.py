# Токен бота
TOKEN = "7729255105:AAEHP1FxcuvwmuJAXpIwJiD5F9BaS-1DQ0s"

# Этапы диалога
CITY, SERVICE, REPAIR_DETAILS, CHOOSE_SERVICE_CENTER, CHOOSE_DATE, CHOOSE_TIME, ENTER_NAME, ENTER_PHONE, DEVICE_IN_SERVICE = range(9)

API_URL = 'http://api'

# Регулярные выражения для валидации
ORDER_REGEX = r'^\d{3}-\d{5}$'
PHONE_REGEX = r'^7\d{10}$'
NAME_REGEX = r'^[a-zA-Zа-яА-Я\s]+$'  # Только буквы и пробелы