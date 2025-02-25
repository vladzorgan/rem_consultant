from typing import List, Optional, Tuple, Dict, Any
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.repair import (
    RepairRepository, RepairTypeRepository, PartRepository,
    RepairPartRepository, ModelRepairRepository, RepairPriceRepository,
    PriceRepository
)
from app.schemas.repair import (
    RepairCreate, RepairUpdate, Repair,
    RepairTypeCreate, RepairTypeUpdate, RepairType,
    PriceAnalysis
)


class RepairService:
    def __init__(self):
        self.repair_repository = RepairRepository()
        self.repair_type_repository = RepairTypeRepository()

    # -- Операции с ремонтами --

    async def get_repair(self, db: AsyncSession, repair_id: int) -> Repair:
        """Получить ремонт по ID"""
        repair = await self.repair_repository.get(db, repair_id)
        if not repair:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Ремонт с ID {repair_id} не найден"
            )
        return repair

    async def get_repair_with_types(self, db: AsyncSession, repair_id: int) -> Repair:
        """Получить ремонт с его типами по ID"""
        repair = await self.repair_repository.get_with_types(db, repair_id)
        if not repair:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Ремонт с ID {repair_id} не найден"
            )
        return repair

    async def get_repairs(
            self, db: AsyncSession, skip: int = 0, limit: int = 100
    ) -> Tuple[List[Repair], int]:
        """Получить список ремонтов с пагинацией"""
        repairs = await self.repair_repository.get_multi(db, skip=skip, limit=limit)
        total = await self.repair_repository.get_count(db)
        return repairs, total

    async def search_repairs(
            self, db: AsyncSession, keyword: str, skip: int = 0, limit: int = 100
    ) -> Tuple[List[Repair], int]:
        """Поиск ремонтов по ключевому слову"""
        repairs = await self.repair_repository.search(db, keyword=keyword, skip=skip, limit=limit)

        # Для получения общего числа совпадений используем отдельный запрос
        from sqlalchemy import or_, func
        query = self.repair_repository.model.__table__.select().where(
            or_(
                func.lower(self.repair_repository.model.name).contains(func.lower(keyword)),
                func.lower(self.repair_repository.model.description).contains(func.lower(keyword))
            )
        )
        total = await self.repair_repository.get_count(db, query)
        return repairs, total

    async def create_repair(self, db: AsyncSession, repair_in: RepairCreate) -> Repair:
        """Создать новый ремонт"""
        # Проверяем, существует ли ремонт с таким названием
        existing_repair = await self.repair_repository.get_by_name(db, repair_in.name)
        if existing_repair:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ремонт с названием '{repair_in.name}' уже существует"
            )

        return await self.repair_repository.create(db, obj_in=repair_in)

    async def update_repair(
            self, db: AsyncSession, repair_id: int, repair_in: RepairUpdate
    ) -> Repair:
        """Обновить существующий ремонт"""
        repair = await self.get_repair(db, repair_id)

        # Если обновляется название, проверяем уникальность
        if repair_in.name and repair_in.name != repair.name:
            existing_repair = await self.repair_repository.get_by_name(db, repair_in.name)
            if existing_repair:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Ремонт с названием '{repair_in.name}' уже существует"
                )

        return await self.repair_repository.update(db, db_obj=repair, obj_in=repair_in)

    async def delete_repair(self, db: AsyncSession, repair_id: int) -> Repair:
        """Удалить ремонт по ID"""
        repair = await self.get_repair(db, repair_id)
        return await self.repair_repository.remove(db, id=repair_id)

    # -- Операции с типами ремонтов --

    async def get_repair_type(self, db: AsyncSession, repair_type_id: int) -> RepairType:
        """Получить тип ремонта по ID"""
        repair_type = await self.repair_type_repository.get(db, repair_type_id)
        if not repair_type:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Тип ремонта с ID {repair_type_id} не найден"
            )
        return repair_type

    async def get_repair_type_with_parts(self, db: AsyncSession, repair_type_id: int) -> RepairType:
        """Получить тип ремонта с его запчастями по ID"""
        repair_type = await self.repair_type_repository.get_with_repair_parts(db, repair_type_id)
        if not repair_type:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Тип ремонта с ID {repair_type_id} не найден"
            )
        return repair_type

    async def get_repair_types(
            self, db: AsyncSession, skip: int = 0, limit: int = 100
    ) -> Tuple[List[RepairType], int]:
        """Получить список типов ремонтов с пагинацией"""
        repair_types = await self.repair_type_repository.get_multi(db, skip=skip, limit=limit)
        total = await self.repair_type_repository.get_count(db)
        return repair_types, total

    async def get_repair_types_by_group(
            self, db: AsyncSession, group_name: str, skip: int = 0, limit: int = 100
    ) -> Tuple[List[RepairType], int]:
        """Получить список типов ремонтов по группе с пагинацией"""
        repair_types = await self.repair_type_repository.get_by_group(
            db, group_name=group_name, skip=skip, limit=limit
        )

        # Получаем общее число типов для этой группы
        from sqlalchemy import select, func
        query = select(func.count()).where(
            func.lower(self.repair_type_repository.model.group_name) == func.lower(group_name)
        ).select_from(self.repair_type_repository.model)

        result = await db.execute(query)
        total = result.scalar_one()

        return repair_types, total

    async def search_repair_types(
            self, db: AsyncSession, keyword: str, group_name: Optional[str] = None,
            skip: int = 0, limit: int = 100
    ) -> Tuple[List[RepairType], int]:
        """Поиск типов ремонтов по ключевому слову и опционально по группе"""
        repair_types = await self.repair_type_repository.search(
            db, keyword=keyword, group_name=group_name, skip=skip, limit=limit
        )

        # Для получения общего числа совпадений используем отдельный запрос
        from sqlalchemy import or_, and_, func
        conditions = [
            or_(
                func.lower(self.repair_type_repository.model.name).contains(func.lower(keyword)),
                func.lower(self.repair_type_repository.model.description).contains(func.lower(keyword))
            )
        ]

        if group_name:
            conditions.append(
                func.lower(self.repair_type_repository.model.group_name) == func.lower(group_name)
            )

        query = self.repair_type_repository.model.__table__.select().where(and_(*conditions))
        total = await self.repair_type_repository.get_count(db, query)

        return repair_types, total

    async def create_repair_type(self, db: AsyncSession, repair_type_in: RepairTypeCreate) -> RepairType:
        """Создать новый тип ремонта"""
        # Проверяем, существует ли тип ремонта с таким названием в этой группе
        existing_type = await self.repair_type_repository.get_by_name(
            db, name=repair_type_in.name, group_name=repair_type_in.group_name
        )

        if existing_type:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Тип ремонта с названием '{repair_type_in.name}' уже существует в группе '{repair_type_in.group_name}'"
            )

        return await self.repair_type_repository.create(db, obj_in=repair_type_in)

    async def update_repair_type(
            self, db: AsyncSession, repair_type_id: int, repair_type_in: RepairTypeUpdate
    ) -> RepairType:
        """Обновить существующий тип ремонта"""
        repair_type = await self.get_repair_type(db, repair_type_id)

        # Проверяем уникальность, если изменяется название или группа
        if (repair_type_in.name and repair_type_in.name != repair_type.name) or \
                (repair_type_in.group_name and repair_type_in.group_name != repair_type.group_name):

            name = repair_type_in.name or repair_type.name
            group_name = repair_type_in.group_name or repair_type.group_name

            existing_type = await self.repair_type_repository.get_by_name(
                db, name=name, group_name=group_name
            )

            if existing_type and existing_type.id != repair_type_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Тип ремонта с названием '{name}' уже существует в группе '{group_name}'"
                )

        return await self.repair_type_repository.update(db, db_obj=repair_type, obj_in=repair_type_in)

    async def delete_repair_type(self, db: AsyncSession, repair_type_id: int) -> RepairType:
        """Удалить тип ремонта по ID"""
        repair_type = await self.get_repair_type(db, repair_type_id)
        return await self.repair_type_repository.remove(db, id=repair_type_id)


# Экспортируем экземпляр сервиса для использования в API
repair_service = RepairService()