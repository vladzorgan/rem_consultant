from typing import Generator, AsyncGenerator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt
from pydantic import ValidationError

from app.db.session import get_async_db
from app.models.user import User
from app.schemas.user import UserRole
from app.core.config import settings
from app.core.auth import decode_token
from app.services.user_service import user_service

# Реэкспорт зависимости для базы данных
get_async_db = get_async_db

# Настройка OAuth2
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login",
    auto_error=False  # Устанавливаем auto_error на уровне схемы, а не Security
)


async def get_current_user(
        db: AsyncSession = Depends(get_async_db),
        token: str = Depends(oauth2_scheme),
) -> User:
    """
    Получить текущего аутентифицированного пользователя.
    """
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Не предоставлены учетные данные",
            headers={"WWW-Authenticate": "Bearer"},
        )

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Не удалось проверить учетные данные",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Декодируем JWT токен
    payload = decode_token(token)
    if payload is None:
        raise credentials_exception

    # Получаем ID пользователя из токена
    user_id = int(payload.get("sub"))
    if user_id is None:
        raise credentials_exception

    # Получаем пользователя из базы данных
    user = await user_service.get_user(db, user_id)
    if user is None:
        raise credentials_exception

    # Проверяем, что пользователь активен
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь неактивен"
        )

    return user


async def get_current_service_owner(
        current_user: User = Depends(get_current_user),
) -> User:
    """
    Проверяет, что текущий пользователь является владельцем сервисного центра.
    """
    if current_user.role != UserRole.SERVICE_OWNER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для выполнения операции. Требуется роль владельца сервисного центра."
        )
    return current_user


async def get_current_admin_user(
        current_user: User = Depends(get_current_user),
) -> User:
    """
    Проверяет, что текущий пользователь имеет права администратора.
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для выполнения операции. Требуется роль администратора."
        )
    return current_user


async def get_optional_current_user(
        db: AsyncSession = Depends(get_async_db),
        token: Optional[str] = Depends(oauth2_scheme),
) -> Optional[User]:
    """
    Получить текущего пользователя, если он аутентифицирован, иначе None.
    """
    if token is None:
        return None

    try:
        # Декодируем JWT токен
        payload = decode_token(token)
        if payload is None:
            return None

        # Получаем ID пользователя из токена
        user_id = int(payload.get("sub"))
        if user_id is None:
            return None

        # Получаем пользователя из базы данных
        user = await user_service.get_user(db, user_id)
        if user is None or not user.is_active:
            return None

        return user
    except (jwt.JWTError, ValidationError):
        return None