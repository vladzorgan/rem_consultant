import unittest
from unittest.mock import AsyncMock, MagicMock, patch
from telegram import Update, Message, User
from telegram.ext import ContextTypes, ConversationHandler
import handlers
from utils import normalize_phone

class TestBot(unittest.TestCase):

    def setUp(self):
        """Настройка перед каждым тестом"""
        self.update = MagicMock(spec=Update)
        self.update.message = MagicMock(spec=Message)
        self.update.message.from_user = MagicMock(spec=User)
        self.context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)
        self.context.user_data = {}

    # Тесты для utils.py
    def test_normalize_phone_valid_plus(self):
        """Тест нормализации номера с '+'"""
        result = normalize_phone("+79991234567")
        self.assertEqual(result, "79991234567")

    def test_normalize_phone_valid_8(self):
        """Тест нормализации номера с '8'"""
        result = normalize_phone("89991234567")
        self.assertEqual(result, "79991234567")

    def test_normalize_phone_valid_7(self):
        """Тест нормализации номера с '7'"""
        result = normalize_phone("79991234567")
        self.assertEqual(result, "79991234567")

    def test_normalize_phone_invalid_short(self):
        """Тест нормализации короткого номера"""
        result = normalize_phone("+79991234")
        self.assertIsNone(result)

    def test_normalize_phone_invalid_chars(self):
        """Тест нормализации номера с лишними символами"""
        result = normalize_phone("+7 (999) 123-45-67")
        self.assertEqual(result, "79991234567")

    # Тесты для handlers.py
    @patch('handlers.logger')
    async def test_start(self, mock_logger):
        """Тест обработчика /start"""
        self.update.message.from_user.first_name = "Иван"
        self.update.message.reply_text = AsyncMock()

        result = await handlers.start(self.update, self.context)
        self.assertEqual(result, 0)  # CITY
        self.update.message.reply_text.assert_any_call("Здравствуйте, Иван! Я помогу вам найти лучший сервисный центр для ремонта.\n")
        mock_logger.info.assert_called_with("Пользователь Иван (ID: None) начал диалог")

    @patch('handlers.logger')
    async def test_get_city(self, mock_logger):
        """Тест обработчика города"""
        self.update.message.text = "Краснодар"
        self.update.message.reply_text = AsyncMock()

        result = await handlers.get_city(self.update, self.context)
        self.assertEqual(result, 1)  # SERVICE
        self.assertEqual(self.context.user_data['city'], "Краснодар")
        self.update.message.reply_text.assert_called_once()
        mock_logger.info.assert_called_with("Пользователь (ID: None) ввел город: Краснодар")

    @patch('handlers.logger')
    async def test_enter_name_valid(self, mock_logger):
        """Тест обработчика имени с корректным вводом"""
        self.update.message.text = "Алексей"
        self.update.message.reply_text = AsyncMock()

        result = await handlers.enter_name(self.update, self.context)
        self.assertEqual(result, 7)  # ENTER_PHONE
        self.assertEqual(self.context.user_data['name'], "Алексей")
        self.update.message.reply_text.assert_called_once()
        mock_logger.info.assert_called_with("Пользователь (ID: None) ввел имя: Алексей")

    @patch('handlers.logger')
    async def test_enter_name_invalid_short(self, mock_logger):
        """Тест обработчика имени с коротким вводом"""
        self.update.message.text = "А"
        self.update.message.reply_text = AsyncMock()

        result = await handlers.enter_name(self.update, self.context)
        self.assertEqual(result, 6)  # ENTER_NAME
        self.assertNotIn('name', self.context.user_data)
        self.update.message.reply_text.assert_called_with(
            "Некорректное имя. Пожалуйста, введите имя длиной минимум 2 буквы, используя только буквы и пробелы (например, Анна, Иван Петров)."
        )
        mock_logger.warning.assert_called_with("Пользователь (ID: None) ввел некорректное имя: А")

    @patch('handlers.logger')
    async def test_enter_name_invalid_chars(self, mock_logger):
        """Тест обработчика имени с недопустимыми символами"""
        self.update.message.text = "Алексей123"
        self.update.message.reply_text = AsyncMock()

        result = await handlers.enter_name(self.update, self.context)
        self.assertEqual(result, 6)  # ENTER_NAME
        self.assertNotIn('name', self.context.user_data)
        self.update.message.reply_text.assert_called_with(
            "Некорректное имя. Пожалуйста, введите имя длиной минимум 2 буквы, используя только буквы и пробелы (например, Анна, Иван Петров)."
        )
        mock_logger.warning.assert_called_with("Пользователь (ID: None) ввел некорректное имя: Алексей123")

    @patch('handlers.logger')
    async def test_device_in_service_valid_order(self, mock_logger):
        """Тест обработчика 'Мое устройство в сервисе' с корректным номером заказа"""
        self.update.message.text = "253-59912"
        self.update.message.reply_text = AsyncMock()
        self.context.user_data['city'] = "Краснодар"
        self.context.user_data['service'] = "Мое устройство в сервисе"

        result = await handlers.device_in_service(self.update, self.context)
        self.assertEqual(result, ConversationHandler.END)
        self.assertEqual(self.context.user_data['order_or_phone'], "253-59912")
        self.update.message.reply_text.assert_called_once()
        mock_logger.info.assert_any_call("Пользователь (ID: None) завершил диалог с услугой: Мое устройство в сервисе, ввел номер заказа: 253-59912")

    @patch('handlers.logger')
    async def test_device_in_service_invalid(self, mock_logger):
        """Тест обработчика 'Мое устройство в сервисе' с некорректным вводом"""
        self.update.message.text = "12345"
        self.update.message.reply_text = AsyncMock()
        self.context.user_data['city'] = "Краснодар"
        self.context.user_data['service'] = "Мое устройство в сервисе"

        result = await handlers.device_in_service(self.update, self.context)
        self.assertEqual(result, 8)  # DEVICE_IN_SERVICE
        self.assertNotIn('order_or_phone', self.context.user_data)
        self.update.message.reply_text.assert_called_with(
            "Некорректный формат. Пожалуйста, введите номер заказа в формате XXX-XXXXX (например, 253-59912) "
            "или контактный номер телефона в формате 79999999999 (например, 79217578234)."
        )
        mock_logger.warning.assert_called_with("Пользователь (ID: None) ввел некорректные данные для 'Мое устройство в сервисе': 12345")

if __name__ == "__main__":
    unittest.main()