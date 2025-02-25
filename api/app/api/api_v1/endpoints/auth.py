from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_async_db, get_current_user
from app.services.user_service import user_service
from app.schemas.user import UserCreate, Token, User, UserChangePassword

router = APIRouter()


@router.post("/login", response_model=Token)
async def login_access_token(
    db: AsyncSession = Depends(get_async_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Any:
    """
    Получение OAuth2 совместимого токена для доступа к API
    """
    return await user_service.authenticate(
        db, email=form_data.username, password=form_data.password
    )


@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_async_db),
) -> Any:
    """
    Регистрация нового пользователя
    """
    return await user_service.register_user(db, user_data=user_in)


@router.get("/me", response_model=User)
async def read_users_me(
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Получить текущего пользователя
    """
    return current_user


@router.put("/me/password", response_model=User)
async def change_password(
    password_data: UserChangePassword,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
) -> Any:
    """
    Изменить пароль текущего пользователя
    """
    return await user_service.change_password(
        db, user_id=current_user.id, password_data=password_data
    )


@router.put("/me", response_model=User)
async def update_user_me(
    user_in: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
) -> Any:
    """
    Обновить информацию о текущем пользователе
    (email, full_name, phone)
    """
    return await user_service.update_user(
        db, user_id=current_user.id, user_in=user_in
    )