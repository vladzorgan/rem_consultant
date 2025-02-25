# /app/app/schemas/bot_log.py
from pydantic import BaseModel
from typing import Any
from datetime import datetime

class BotLogCreateSchema(BaseModel):
    telegram_user_id: int
    request_text: str
    response_text: Any  # Может быть dict, str или другой тип, в зависимости от ответа

class BotLogResponseSchema(BaseModel):
    id: int
    telegram_user_id: int
    request_text: str
    response_text: Any
    created_at: datetime
    updated_at: datetime  # Добавлено для соответствия модели

    class Config:
        from_attributes = True