# Используем официальный образ Python
FROM python:3.9-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем requirements.txt и устанавливаем зависимости
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Копируем исходный код бота
COPY . /app/

# Устанавливаем переменные окружения
ENV PYTHONPATH=/app

# Запускаем бота
CMD ["python", "app/bot.py"]
