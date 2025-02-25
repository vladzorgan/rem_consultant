from sqlalchemy import Column, Integer, String, JSON, Index, ForeignKey
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.models.common import TimestampMixin


class BotLog(Base, TimestampMixin):
    __tablename__ = "bot_logs"

    id = Column(Integer, primary_key=True)
    telegram_user_id = Column(Integer, ForeignKey('users.telegram_id'), nullable=False)
    request_text = Column(String, nullable=False)
    response_text = Column(JSON, nullable=False)

    # Дополнительные поля для расширенного логирования
    session_id = Column(String, nullable=True)  # Для группировки запросов в одну сессию
    command = Column(String, nullable=True)  # Команда бота, если применимо
    status = Column(String, nullable=True)  # Статус обработки (успех/ошибка)

    # Отношения
    user = relationship("User")

    __table_args__ = (
        Index('idx_bot_log_telegram_user_id', 'telegram_user_id'),
        Index('idx_bot_log_session_id', 'session_id'),
    )

    def __repr__(self):
        return f"<BotLog(id={self.id}, telegram_user_id={self.telegram_user_id})>"


class ApiLog(Base, TimestampMixin):
    __tablename__ = "api_logs"

    id = Column(Integer, primary_key=True)
    endpoint = Column(String, nullable=False)
    method = Column(String, nullable=False)
    request_data = Column(JSON, nullable=True)
    response_data = Column(JSON, nullable=True)
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    response_time = Column(Integer, nullable=True)  # в миллисекундах
    status_code = Column(Integer, nullable=True)

    __table_args__ = (
        Index('idx_api_log_endpoint', 'endpoint'),
        Index('idx_api_log_method', 'method'),
        Index('idx_api_log_status_code', 'status_code'),
    )

    def __repr__(self):
        return f"<ApiLog(id={self.id}, endpoint='{self.endpoint}', method='{self.method}', status_code={self.status_code})>"