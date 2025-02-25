from datetime import datetime, timedelta
from typing import Optional, Union, Any

from jose import jwt
from passlib.context import CryptContext
from pydantic import ValidationError

from app.core.config import settings
from app.schemas.user import Token, User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Проверка пароля на соответствие хешу
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Хеширование пароля
    """
    return pwd_context.hash(password)


def create_access_token(subject: Union[str, Any], user: User) -> Token:
    """
    Создание JWT токена доступа
    """
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "type": "access_token",
    }

    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm="HS256"
    )

    return Token(
        access_token=encoded_jwt,
        expires_at=int(expire.timestamp()),
        user=user
    )


def decode_token(token: str) -> Optional[dict]:
    """
    Декодирование JWT токена
    """
    try:
        decoded_token = jwt.decode(
            token, settings.SECRET_KEY, algorithms=["HS256"]
        )

        # Проверка срока действия токена
        if datetime.fromtimestamp(decoded_token["exp"]) < datetime.utcnow():
            return None

        return decoded_token

    except (jwt.JWTError, ValidationError):
        return None