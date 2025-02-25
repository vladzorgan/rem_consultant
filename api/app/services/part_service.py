from typing import List, Optional, Tuple, Dict, Any
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.repair import PartRepository, RepairPartRepository
from app.schemas.repair import (
    PartCreate, PartUpdate, Part,
    RepairPartCreate, RepairPartUpdate, RepairPart
)


class PartService:
    def __init__(self):
        self.part_repository = PartRepository()
        self.repair_part_repository = RepairPartRepository()

    # -- Операции с запчастями --

    async def get_part(self, db: AsyncSession, part_id: int) -> Part:
        """Получить запчасть по ID"""
        part = await self.part_repository.get(db, part_id)
        if not part:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Запчасть с ID {part_id} не найдена"
            )
        return part

    async def get_part_by_sku(self, db: AsyncSession, sku: str) -> Part:
        """Получить запчасть по артикулу (SKU)"""
        part = await self.part_repository.get_by_sku(db, sku)
        if not part:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Запчасть с артикулом '{sku}' не найдена"
            )
        return part

    async def get_parts(
            self, db: AsyncSession, skip: int = 0, limit: int = 100
    ) -> Tuple[List[Part], int]:
        """Получить список запчастей с пагинацией"""
        parts = await self.part_repository.get_multi(db, skip=skip, limit=limit)
        total = await self.part_repository.get_count(db)
        return parts, total

    async def get_parts_by_price_range(
            self, db: AsyncSession, min_price: float = 0, max_price: Optional[float] = None,
            skip: int = 0, limit: int = 100
    ) -> Tuple[List[Part], int]:
        """Получить запчасти в заданном диапазоне цен"""
        parts = await self.part_repository.get_by_price_range(
            db, min_price=min_price, max_price=max_price, skip=skip, limit=limit
        )

        # Получаем общее число запчастей в заданном диапазоне
        from sqlalchemy import and_
        conditions = [self.part_repository.model.retail_price >= min_price]

        if max_price is not None:
            conditions.append(self.part_repository.model.retail_price <= max_price)

        query = self.part_repository.model.__table__.select().where(and_(*conditions))
        total = await self.part_repository.get_count(db, query)

        return parts, total

    async def search_parts(
            self, db: AsyncSession, keyword: str, skip: int = 0, limit: int = 100
    ) -> Tuple[List[Part], int]:
        """Поиск запчастей по ключевому слову"""
        parts = await self.part_repository.search(db, keyword=keyword, skip=skip, limit=limit)

        # Для получения общего числа совпадений используем отдельный запрос
        from sqlalchemy import or_, func
        query = self.part_repository.model.__table__.select().where(
            or_(
                func.lower(self.part_repository.model.name).contains(func.lower(keyword)),
                func.lower(self.part_repository.model.description).contains(func.lower(keyword)),
                func.lower(self.part_repository.model.sku).contains(func.lower(keyword)),
                func.lower(self.part_repository.model.manufacturer).contains(func.lower(keyword))
            )
        )
        total = await self.part_repository.get_count(db, query)

        return parts, total

    async def create_part(self, db: AsyncSession, part_in: PartCreate) -> Part:
        """Создать новую запчасть"""
        # Проверяем уникальность SKU, если он указан
        if part_in.sku:
            existing_part = await self.part_repository.get_by_sku(db, part_in.sku)
            if existing_part:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Запчасть с артикулом '{part_in.sku}' уже существует"
                )

        return await self.part_repository.create(db, obj_in=part_in)

    async def update_part(
            self, db: AsyncSession, part_id: int, part_in: PartUpdate
    ) -> Part:
        """Обновить существующую запчасть"""
        part = await self.get_part(db, part_id)

        # Проверяем уникальность SKU, если он изменяется
        if part_in.sku and part_in.sku != part.sku:
            existing_part = await self.part_repository.get_by_sku(db, part_in.sku)
            if existing_part:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Запчасть с артикулом '{part_in.sku}' уже существует"
                )

        return await self.part_repository.update(db, db_obj=part, obj_in=part_in)

    async def delete_part(self, db: AsyncSession, part_id: int) -> Part:
        """Удалить запчасть по ID"""
        part = await self.get_part(db, part_id)
        return await self.part_repository.remove(db, id=part_id)

    # -- Операции с RepairPart (связь ремонт-запчасть) --

    async def get_repair_part(self, db: AsyncSession, repair_part_id: int) -> RepairPart:
        """Получить связь ремонт-запчасть по ID"""
        repair_part = await self.repair_part_repository.get(db, repair_part_id)
        if not repair_part:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Связь ремонт-запчасть с ID {repair_part_id} не найдена"
            )
        return repair_part

    async def get_repair_part_with_part(self, db: AsyncSession, repair_part_id: int) -> RepairPart:
        """Получить связь ремонт-запчасть с данными о запчасти"""
        repair_part = await self.repair_part_repository.get_with_part(db, repair_part_id)
        if not repair_part:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Связь ремонт-запчасть с ID {repair_part_id} не найдена"
            )
        return repair_part

    async def get_repair_parts_by_repair_type(
            self, db: AsyncSession, repair_type_id: int, skip: int = 0, limit: int = 100
    ) -> Tuple[List[RepairPart], int]:
        """Получить запчасти для типа ремонта"""
        repair_parts = await self.repair_part_repository.get_by_repair_type(
            db, repair_type_id=repair_type_id, skip=skip, limit=limit
        )

        # Получаем общее число запчастей для этого типа ремонта
        from sqlalchemy import select, func
        query = select(func.count()).where(
            self.repair_part_repository.model.repair_type_id == repair_type_id
        ).select_from(self.repair_part_repository.model)

        result = await db.execute(query)
        total = result.scalar_one()

        return repair_parts, total

    async def create_repair_part(self, db: AsyncSession, repair_part_in: RepairPartCreate) -> RepairPart:
        """Добавить запчасть к типу ремонта"""
        # Проверяем, существует ли уже такая связь
        existing_repair_part = await self.repair_part_repository.get_by_repair_type_and_part(
            db, repair_type_id=repair_part_in.repair_type_id, part_id=repair_part_in.part_id
        )

        if existing_repair_part:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Эта запчасть уже добавлена к данному типу ремонта"
            )

        # Проверяем существование связанных сущностей (тип ремонта и запчасть)
        from app.services.repair_service import repair_service

        # Проверка существования типа ремонта
        await repair_service.get_repair_type(db, repair_part_in.repair_type_id)

        # Проверка существования запчасти
        await self.get_part(db, repair_part_in.part_id)

        return await self.repair_part_repository.create(db, obj_in=repair_part_in)

    async def update_repair_part(
            self, db: AsyncSession, repair_part_id: int, repair_part_in: RepairPartUpdate
    ) -> RepairPart:
        """Обновить связь ремонт-запчасть"""
        repair_part = await self.get_repair_part(db, repair_part_id)

        # Если меняется тип ремонта или запчасть, проверяем уникальность связи
        if (repair_part_in.repair_type_id and repair_part_in.repair_type_id != repair_part.repair_type_id) or \
                (repair_part_in.part_id and repair_part_in.part_id != repair_part.part_id):

            repair_type_id = repair_part_in.repair_type_id or repair_part.repair_type_id
            part_id = repair_part_in.part_id or repair_part.part_id

            existing_repair_part = await self.repair_part_repository.get_by_repair_type_and_part(
                db, repair_type_id=repair_type_id, part_id=part_id
            )

            if existing_repair_part and existing_repair_part.id != repair_part_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Эта запчасть уже добавлена к данному типу ремонта"
                )

            # Проверяем существование связанных сущностей
            from app.services.repair_service import repair_service

            if repair_part_in.repair_type_id:
                await repair_service.get_repair_type(db, repair_part_in.repair_type_id)

            if repair_part_in.part_id:
                await self.get_part(db, repair_part_in.part_id)

        return await self.repair_part_repository.update(db, db_obj=repair_part, obj_in=repair_part_in)

    async def delete_repair_part(self, db: AsyncSession, repair_part_id: int) -> RepairPart:
        """Удалить связь ремонт-запчасть"""
        repair_part = await self.get_repair_part(db, repair_part_id)
        return await self.repair_part_repository.remove(db, id=repair_part_id)


# Экспортируем экземпляр сервиса для использования в API
part_service = PartService()