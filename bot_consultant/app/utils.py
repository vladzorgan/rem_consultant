import re

def normalize_phone(phone: str) -> str:
    """Нормализация номера телефона в формат 79999999999"""
    digits = re.sub(r'\D', '', phone)
    if digits.startswith('8') and len(digits) == 11:
        digits = '7' + digits[1:]
    if digits.startswith('7') and len(digits) == 11:
        return digits
    return None