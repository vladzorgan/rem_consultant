from typing import List, Optional, Tuple
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import EmailStr

from app.repositories.users import UserRepository
from app.schemas.user import UserCreate, UserUpdate, User, UserRole, Token, UserChangePassword
from app.models.user import User as UserModel
from app.core.auth import create_access_token, verify_password


class UserService:
    def __init__(self):
        self.repository = UserRepository()

    # -- Операции аутентификации --

    async def authenticate(self, db: AsyncSession, email: str, password: str) -> Token:
        """Аутентификация пользователя и создание токена"""
        user = await self.repository.authenticate(db, email=email, password=password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверный email или пароль",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Пользователь неактивен"
            )

        # Создаем JWT токен
        return create_access_token(subject=user.id, user=user)

    async def register_user(self, db: AsyncSession, user_data: UserCreate) -> User:
        """Регистрация нового пользователя"""
        # Проверяем, что пароли совпадают
        if user_data.password != user_data.password_confirm:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Пароли не совпадают"
            )

        # Проверяем, что пользователь с таким email не существует
        existing_user = await self.repository.get_by_email(db, email=user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Пользователь с email {user_data.email} уже существует"
            )

        # Создаем пользователя
        user = await self.repository.create_user(db, obj_in=user_data)
        return user

    async def change_password(
            self, db: AsyncSession, user_id: int, password_data: UserChangePassword
    ) -> User:
        """Смена пароля пользователя"""
        user = await self.repository.get(db, id=user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Пользователь с ID {user_id} не найден"
            )

        # Проверяем текущий пароль
        if not verify_password(password_data.current_password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Неверный текущий пароль"
            )

        # Проверяем, что новые пароли совпадают
        if password_data.new_password != password_data.new_password_confirm:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Новые пароли не совпадают"
            )

        # Обновляем пароль
        return await self.repository.update_password(
            db, db_obj=user, new_password=password_data.new_password
        )

    # -- CRUD операции --

    async def get_user(self, db: AsyncSession, user_id: int) -> User:
        """Получить пользователя по ID"""
        user = await self.repository.get(db, id=user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Пользователь с ID {user_id} не найден"
            )
        return user

    async def get_user_by_email(self, db: AsyncSession, email: EmailStr) -> Optional[User]:
        """Получить пользователя по email"""
        return await self.repository.get_by_email(db, email=email)

    async def get_users(
            self, db: AsyncSession, skip: int = 0, limit: int = 100
    ) -> Tuple[List[User], int]:
        """Получить список пользователей с пагинацией"""
        users = await self.repository.get_multi(db, skip=skip, limit=limit)
        total = await self.repository.get_count(db)
        return users, total

    async def search_users(
            self, db: AsyncSession, keyword: str, skip: int = 0, limit: int = 100
    ) -> Tuple[List[User], int]:
        """Поиск пользователей по ключевому слову"""
        users = await self.repository.search_users(db, keyword=keyword, skip=skip, limit=limit)

        # Для получения общего числа совпадений
        from sqlalchemy import or_, func, select
        query = select(func.count()).where(
            or_(
                func.lower(UserModel.email).contains(func.lower(keyword)),
                func.lower(UserModel.full_name).contains(func.lower(keyword))
            )
        ).select_from(UserModel)

        result = await db.execute(query)
        total = result.scalar_one()

        return users, total

    async def update_user(
            self, db: AsyncSession, user_id: int, user_in: UserUpdate
    ) -> User:
        """Обновить данные пользователя"""
        user = await self.get_user(db, user_id)

        # Если обновляется email, проверяем его уникальность
        if user_in.email and user_in.email != user.email:
            existing_user = await self.repository.get_by_email(db, email=user_in.email)
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Пользователь с email {user_in.email} уже существует"
                )

        return await self.repository.update(db, db_obj=user, obj_in=user_in)

    async def deactivate_user(self, db: AsyncSession, user_id: int) -> User:
        """Деактивировать пользователя"""
        user = await self.get_user(db, user_id)
        user_in = {"is_active": False}
        return await self.repository.update(db, db_obj=user, obj_in=user_in)

    async def delete_user(self, db: AsyncSession, user_id: int) -> User:
        """Удалить пользователя"""
        user = await self.get_user(db, user_id)
        return await self.repository.remove(db, id=user_id)

    async def get_service_owners(
            self, db: AsyncSession, skip: int = 0, limit: int = 100
    ) -> Tuple[List[User], int]:
        """Получить список владельцев сервисных центров"""
        owners = await self.repository.get_service_owners(db, skip=skip, limit=limit)
        total = await self.repository.count_users_by_role(db, UserRole.SERVICE_OWNER)
        return owners, total


# Экземпляр сервиса для использования в API
user_service = UserService()