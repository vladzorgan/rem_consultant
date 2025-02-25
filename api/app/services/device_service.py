from typing import List, Optional, Dict, Any, Tuple
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.devices import DeviceBrandRepository, DeviceModelRepository
from app.schemas.device import (
    DeviceBrandCreate, DeviceBrandUpdate, DeviceBrand, DeviceBrandWithModels,
    DeviceModelCreate, DeviceModelUpdate, DeviceModel
)


class DeviceService:
    def __init__(self):
        self.brand_repository = DeviceBrandRepository()
        self.model_repository = DeviceModelRepository()

    # -- Операции с брендами устройств --

    async def get_brand(self, db: AsyncSession, brand_id: int) -> DeviceBrand:
        """Получить бренд по ID"""
        brand = await self.brand_repository.get(db, brand_id)
        if not brand:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Бренд с ID {brand_id} не найден"
            )
        return brand

    async def get_brand_with_models(self, db: AsyncSession, brand_id: int) -> DeviceBrandWithModels:
        """Получить бренд с его моделями по ID"""
        brand = await self.brand_repository.get_with_models(db, brand_id)
        if not brand:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Бренд с ID {brand_id} не найден"
            )
        return brand

    async def get_brands(
            self, db: AsyncSession, skip: int = 0, limit: int = 100
    ) -> Tuple[List[DeviceBrand], int]:
        """Получить список брендов с пагинацией"""
        brands = await self.brand_repository.get_multi(db, skip=skip, limit=limit)
        total = await self.brand_repository.get_count(db)
        return brands, total

    async def search_brands(
            self, db: AsyncSession, keyword: str, skip: int = 0, limit: int = 100
    ) -> Tuple[List[DeviceBrand], int]:
        """Поиск брендов по ключевому слову"""
        brands = await self.brand_repository.search(db, keyword=keyword, skip=skip, limit=limit)
        # Для получения общего числа совпадений используем отдельный запрос
        query = self.brand_repository.model.__table__.select().where(
            self.brand_repository.model.name.ilike(f"%{keyword}%")
        )
        total = await self.brand_repository.get_count(db, query)
        return brands, total

    async def create_brand(self, db: AsyncSession, brand_in: DeviceBrandCreate) -> DeviceBrand:
        """Создать новый бренд"""
        # Проверяем, существует ли бренд с таким названием
        existing_brand = await self.brand_repository.get_by_name(db, brand_in.name)
        if existing_brand:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Бренд с названием '{brand_in.name}' уже существует"
            )

        return await self.brand_repository.create(db, obj_in=brand_in)

    async def update_brand(
            self, db: AsyncSession, brand_id: int, brand_in: DeviceBrandUpdate
    ) -> DeviceBrand:
        """Обновить существующий бренд"""
        brand = await self.get_brand(db, brand_id)

        # Если обновляется название, проверяем уникальность
        if brand_in.name and brand_in.name != brand.name:
            existing_brand = await self.brand_repository.get_by_name(db, brand_in.name)
            if existing_brand:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Бренд с названием '{brand_in.name}' уже существует"
                )

        return await self.brand_repository.update(db, db_obj=brand, obj_in=brand_in)

    async def delete_brand(self, db: AsyncSession, brand_id: int) -> DeviceBrand:
        """Удалить бренд по ID"""
        brand = await self.get_brand(db, brand_id)
        return await self.brand_repository.remove(db, id=brand_id)

    # -- Операции с моделями устройств --

    async def get_model(self, db: AsyncSession, model_id: int) -> DeviceModel:
        """Получить модель устройства по ID"""
        model = await self.model_repository.get(db, model_id)
        if not model:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Модель с ID {model_id} не найдена"
            )
        return model

    async def get_model_with_brand(self, db: AsyncSession, model_id: int) -> DeviceModel:
        """Получить модель устройства с информацией о бренде"""
        model = await self.model_repository.get_with_brand(db, model_id)
        if not model:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Модель с ID {model_id} не найдена"
            )
        return model

    async def get_models(
            self, db: AsyncSession, skip: int = 0, limit: int = 100
    ) -> Tuple[List[DeviceModel], int]:
        """Получить список моделей с пагинацией"""
        models = await self.model_repository.get_multi(db, skip=skip, limit=limit)
        total = await self.model_repository.get_count(db)
        return models, total

    async def get_models_by_brand(
            self, db: AsyncSession, brand_id: int, skip: int = 0, limit: int = 100
    ) -> Tuple[List[DeviceModel], int]:
        """Получить модели по ID бренда"""
        # Проверяем, существует ли бренд
        brand = await self.brand_repository.get(db, brand_id)
        if not brand:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Бренд с ID {brand_id} не найден"
            )

        models = await self.model_repository.get_by_brand_id(db, brand_id=brand_id, skip=skip, limit=limit)
        # Получаем общее число моделей для этого бренда
        query = self.model_repository.model.__table__.select().where(
            self.model_repository.model.device_brand_id == brand_id
        )
        total = await self.model_repository.get_count(db, query)
        return models, total

    async def search_models(
            self, db: AsyncSession, keyword: str, brand_id: Optional[int] = None, skip: int = 0, limit: int = 100
    ) -> Tuple[List[DeviceModel], int]:
        """Поиск моделей по ключевому слову и опционально по бренду"""
        models = await self.model_repository.search(
            db, keyword=keyword, brand_id=brand_id, skip=skip, limit=limit
        )

        # Формируем условие для подсчета общего числа совпадений
        from sqlalchemy import or_, func
        conditions = [func.lower(self.model_repository.model.name).contains(func.lower(keyword))]

        if brand_id is not None:
            conditions.append(self.model_repository.model.device_brand_id == brand_id)

        query = self.model_repository.model.__table__.select().where(or_(*conditions))
        total = await self.model_repository.get_count(db, query)

        return models, total

    async def create_model(self, db: AsyncSession, model_in: DeviceModelCreate) -> DeviceModel:
        """Создать новую модель устройства"""
        # Проверяем, существует ли бренд
        brand = await self.brand_repository.get(db, model_in.device_brand_id)
        if not brand:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Бренд с ID {model_in.device_brand_id} не найден"
            )

        return await self.model_repository.create(db, obj_in=model_in)

    async def update_model(
            self, db: AsyncSession, model_id: int, model_in: DeviceModelUpdate
    ) -> DeviceModel:
        """Обновить существующую модель устройства"""
        model = await self.get_model(db, model_id)

        # Если обновляется ID бренда, проверяем его существование
        if model_in.device_brand_id and model_in.device_brand_id != model.device_brand_id:
            brand = await self.brand_repository.get(db, model_in.device_brand_id)
            if not brand:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Бренд с ID {model_in.device_brand_id} не найден"
                )

        return await self.model_repository.update(db, db_obj=model, obj_in=model_in)

    async def delete_model(self, db: AsyncSession, model_id: int) -> DeviceModel:
        """Удалить модель устройства по ID"""
        model = await self.get_model(db, model_id)
        return await self.model_repository.remove(db, id=model_id)


device_service = DeviceService()