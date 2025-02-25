from typing import List, Optional, Dict, Any
from sqlalchemy import select, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.device import DeviceBrand, DeviceModel
from app.schemas.device import DeviceBrandCreate, DeviceBrandUpdate, DeviceModelCreate, DeviceModelUpdate
from app.repositories.base import BaseRepository


class DeviceBrandRepository(BaseRepository[DeviceBrand, DeviceBrandCreate, DeviceBrandUpdate]):
    def __init__(self):
        super().__init__(DeviceBrand)

    async def get_with_models(self, db: AsyncSession, id: int) -> Optional[DeviceBrand]:
        """
        Получить бренд с загрузкой связанных моделей устройств
        """
        query = select(DeviceBrand).where(DeviceBrand.id == id).options(selectinload(DeviceBrand.models))
        result = await db.execute(query)
        return result.scalars().first()

    async def get_by_name(self, db: AsyncSession, name: str) -> Optional[DeviceBrand]:
        """
        Поиск бренда по имени
        """
        query = select(DeviceBrand).where(func.lower(DeviceBrand.name) == func.lower(name))
        result = await db.execute(query)
        return result.scalars().first()

    async def search(
            self, db: AsyncSession, *, keyword: str, skip: int = 0, limit: int = 100
    ) -> List[DeviceBrand]:
        """
        Поиск брендов по ключевому слову
        """
        query = (
            select(DeviceBrand)
            .where(func.lower(DeviceBrand.name).contains(func.lower(keyword)))
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        return result.scalars().all()


class DeviceModelRepository(BaseRepository[DeviceModel, DeviceModelCreate, DeviceModelUpdate]):
    def __init__(self):
        super().__init__(DeviceModel)

    async def get_with_brand(self, db: AsyncSession, id: int) -> Optional[DeviceModel]:
        """
        Получить модель устройства с загрузкой связанного бренда
        """
        query = select(DeviceModel).where(DeviceModel.id == id).options(selectinload(DeviceModel.brand))
        result = await db.execute(query)
        return result.scalars().first()

    async def get_by_brand_id(
            self, db: AsyncSession, *, brand_id: int, skip: int = 0, limit: int = 100
    ) -> List[DeviceModel]:
        """
        Получить модели устройств для заданного бренда
        """
        query = (
            select(DeviceModel)
            .where(DeviceModel.device_brand_id == brand_id)
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        return result.scalars().all()

    async def search(
            self, db: AsyncSession, *, keyword: str, brand_id: Optional[int] = None, skip: int = 0, limit: int = 100
    ) -> List[DeviceModel]:
        """
        Поиск моделей устройств по ключевому слову и опционально по бренду
        """
        conditions = [func.lower(DeviceModel.name).contains(func.lower(keyword))]

        if brand_id is not None:
            conditions.append(DeviceModel.device_brand_id == brand_id)

        query = (
            select(DeviceModel)
            .where(or_(*conditions))
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        return result.scalars().all()

    async def get_by_type(
            self, db: AsyncSession, *, device_type: str, skip: int = 0, limit: int = 100
    ) -> List[DeviceModel]:
        """
        Получить модели устройств по типу
        """
        query = (
            select(DeviceModel)
            .where(DeviceModel.type == device_type)
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        return result.scalars().all()

    async def get_by_name_and_brand(
            self, db: AsyncSession, *, name: str, brand_id: int
    ) -> Optional[DeviceModel]:
        """
        Получить модель по названию и ID бренда
        """
        query = select(DeviceModel).where(
            (func.lower(DeviceModel.name) == func.lower(name)) &
            (DeviceModel.device_brand_id == brand_id)
        )
        result = await db.execute(query)
        return result.scalars().first()

    async def count_by_brand(self, db: AsyncSession, *, brand_id: int) -> int:
        """
        Подсчитать количество моделей для определенного бренда
        """
        query = select(func.count(DeviceModel.id)).where(DeviceModel.device_brand_id == brand_id)
        result = await db.execute(query)
        return result.scalar_one()

    async def get_newest_models(self, db: AsyncSession, *, limit: int = 10) -> List[DeviceModel]:
        """
        Получить самые новые модели устройств
        """
        query = (
            select(DeviceModel)
            .order_by(DeviceModel.release_year.desc(), DeviceModel.id.desc())
            .limit(limit)
        )
        result = await db.execute(query)
        return result.scalars().all()