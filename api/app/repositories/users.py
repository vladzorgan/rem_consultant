from typing import List, Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.repositories.base import BaseRepository
from app.core.auth import get_password_hash, verify_password


class UserRepository(BaseRepository[User, UserCreate, UserUpdate]):
    def __init__(self):
        super().__init__(User)

    async def get_by_email(self, db: AsyncSession, email: str) -> Optional[User]:
        """
        Получить пользователя по email
        """
        query = select(User).where(func.lower(User.email) == func.lower(email))
        result = await db.execute(query)
        return result.scalars().first()

    async def create_user(self, db: AsyncSession, *, obj_in: UserCreate) -> User:
        """
        Создать нового пользователя с хешированием пароля
        """
        hashed_password = get_password_hash(obj_in.password)

        db_obj = User(
            email=obj_in.email,
            hashed_password=hashed_password,
            full_name=obj_in.full_name,
            phone=obj_in.phone,
            is_active=obj_in.is_active,
            role=obj_in.role
        )

        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def authenticate(self, db: AsyncSession, *, email: str, password: str) -> Optional[User]:
        """
        Аутентификация пользователя
        """
        user = await self.get_by_email(db, email=email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    async def update_password(
            self, db: AsyncSession, *, db_obj: User, new_password: str
    ) -> User:
        """
        Обновить пароль пользователя
        """
        hashed_password = get_password_hash(new_password)
        db_obj.hashed_password = hashed_password

        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def get_service_owners(
            self, db: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> List[User]:
        """
        Получить список владельцев сервисных центров
        """
        query = (
            select(User)
            .where(User.role == "service_owner")
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        return result.scalars().all()

    async def search_users(
            self, db: AsyncSession, *, keyword: str, skip: int = 0, limit: int = 100
    ) -> List[User]:
        """
        Поиск пользователей по ключевому слову (email или имя)
        """
        from sqlalchemy import or_

        query = (
            select(User)
            .where(
                or_(
                    func.lower(User.email).contains(func.lower(keyword)),
                    func.lower(User.full_name).contains(func.lower(keyword))
                )
            )
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        return result.scalars().all()

    async def count_users_by_role(self, db: AsyncSession, role: str) -> int:
        """
        Подсчет количества пользователей с определенной ролью
        """
        query = select(func.count()).where(User.role == role).select_from(User)
        result = await db.execute(query)
        return result.scalar_one()