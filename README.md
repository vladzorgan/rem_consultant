# Сервис поиска лучших цен на ремонт техники

Сервис для поиска оптимальных цен на ремонт техники в вашем городе. С помощью этого сервиса вы можете узнать стоимость ремонта вашего устройства и сравнить ее со средней по городу.

## Особенности

- Сравнение цен на ремонт от разных сервисных центров
- Анализ отзывов о сервисных центрах
- Телеграм-бот для удобного доступа к информации
- API для интеграции
- Возможность для владельцев сервисных центров подтвердить права на редактирование информации

## Технологии

- **Backend**: Python, FastAPI, SQLAlchemy, Alembic
- **База данных**: PostgreSQL
- **Парсер**: Beautiful Soup 4
- **Telegram бот**: python-telegram-bot
- **Контейнеризация**: Docker, Docker Compose

## Архитектура

Проект разделен на несколько модулей:

1. **API** - REST API на FastAPI для доступа к данным
2. **Parser** - Парсер для сбора данных о ценах и отзывах
3. **Bot** - Telegram бот для взаимодействия с пользователями
4. **Database** - Слой доступа к базе данных PostgreSQL

## Установка и запуск

### Предварительные требования

- Docker и Docker Compose
- Python 3.11+

### Запуск с Docker Compose

1. Клонируйте репозиторий:
   ```bash
   git clone https://github.com/yourusername/repair-price-service.git
   cd repair-price-service
   ```

2. Создайте файл .env с вашими настройками (используйте .env.example как шаблон)

3. Запустите сервисы с Docker Compose:
   ```bash
   docker-compose up -d
   ```

4. API будет доступно по адресу: http://localhost:8000/api/docs

### Запуск без Docker

1. Настройте PostgreSQL

2. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```

3. Примените миграции:
   ```bash
   alembic upgrade head
   ```

4. Запустите API:
   ```bash
   uvicorn app.main:app --reload
   ```

## Разработка

### Структура проекта

```
/app
├── alembic/                      # Миграции базы данных
├── api/                          # API endpoints
├── core/                         # Ядро приложения
├── db/                           # Доступ к базе данных
├── models/                       # Модели SQLAlchemy
├── repositories/                 # Репозитории для доступа к данным
├── schemas/                      # Pydantic модели для валидации
├── services/                     # Бизнес-логика
└── utils/                        # Утилиты
```

### Запуск тестов

```bash
./run_tests.sh
```

## API документация

После запуска сервиса, документация API доступна по адресу:
- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

## Примеры использования

### Получение списка брендов
```bash
curl -X GET "http://localhost:8000/api/v1/devices/brands/" -H "accept: application/json"
```

### Поиск сервисных центров по городу
```bash
curl -X GET "http://localhost:8000/api/v1/service-centers/?city_id=1" -H "accept: application/json"
```

## Лицензия

MIT