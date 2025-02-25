from typing import List, Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.location import Region, City
from app.schemas.location import RegionCreate, RegionUpdate, CityCreate, CityUpdate
from app.repositories.base import BaseRepository


class RegionRepository(BaseRepository[Region, RegionCreate, RegionUpdate]):
    def __init__(self):
        super().__init__(Region)

    async def get_with_cities(self, db: AsyncSession, id: int) -> Optional[Region]:
        """
        Получить регион с загрузкой связанных городов
        """
        query = select(Region).where(Region.id == id).options(selectinload(Region.cities))
        result = await db.execute(query)
        return result.scalars().first()

    async def get_by_name(self, db: AsyncSession, name: str) -> Optional[Region]:
        """
        Поиск региона по имени
        """
        query = select(Region).where(func.lower(Region.name) == func.lower(name))
        result = await db.execute(query)
        return result.scalars().first()

    async def search(
            self, db: AsyncSession, *, keyword: str, skip: int = 0, limit: int = 100
    ) -> List[Region]:
        """
        Поиск регионов по ключевому слову
        """
        query = (
            select(Region)
            .where(func.lower(Region.name).contains(func.lower(keyword)))
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        return result.scalars().all()


class CityRepository(BaseRepository[City, CityCreate, CityUpdate]):
    def __init__(self):
        super().__init__(City)

    async def get_with_region(self, db: AsyncSession, id: int) -> Optional[City]:
        """
        Получить город с загрузкой связанного региона
        """
        query = select(City).where(City.id == id).options(selectinload(City.region))
        result = await db.execute(query)
        return result.scalars().first()

    async def get_by_region_id(
            self, db: AsyncSession, *, region_id: int, skip: int = 0, limit: int = 100
    ) -> List[City]:
        """
        Получить города для заданного региона
        """
        query = (
            select(City)
            .where(City.region_id == region_id)
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        return result.scalars().all()

    async def search(
            self, db: AsyncSession, *, keyword: str, region_id: Optional[int] = None, skip: int = 0, limit: int = 100
    ) -> List[City]:
        """
        Поиск городов по ключевому слову и опционально по региону
        """
        from sqlalchemy import or_

        conditions = [func.lower(City.name).contains(func.lower(keyword))]

        if region_id is not None:
            conditions.append(City.region_id == region_id)

        query = (
            select(City)
            .where(or_(*conditions))
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        return result.scalars().all()

    async def get_by_name_and_region(
            self, db: AsyncSession, *, name: str, region_id: Optional[int] = None
    ) -> Optional[City]:
        """
        Получить город по названию и опционально по региону
        """
        conditions = [func.lower(City.name) == func.lower(name)]

        if region_id is not None:
            conditions.append(City.region_id == region_id)

        query = select(City).where(*conditions)
        result = await db.execute(query)
        return result.scalars().first()

    async def get_largest_cities(
            self, db: AsyncSession, *, limit: int = 10
    ) -> List[City]:
        """
        Получить города с наибольшей численностью населения
        """
        query = (
            select(City)
            .order_by(City.population.desc())
            .limit(limit)
        )
        result = await db.execute(query)
        return result.scalars().all()