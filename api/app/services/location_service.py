from typing import List, Optional, Tuple
from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.location import RegionRepository, CityRepository
from app.schemas.location import (
    RegionCreate, RegionUpdate, Region, RegionWithCities,
    CityCreate, CityUpdate, City
)


class LocationService:
    def __init__(self):
        self.region_repository = RegionRepository()
        self.city_repository = CityRepository()

    # -- Операции с регионами --

    async def get_region(self, db: AsyncSession, region_id: int) -> Region:
        """Получить регион по ID"""
        region = await self.region_repository.get(db, region_id)
        if not region:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Регион с ID {region_id} не найден"
            )
        return region

    async def get_region_with_cities(self, db: AsyncSession, region_id: int) -> RegionWithCities:
        """Получить регион с его городами по ID"""
        region = await self.region_repository.get_with_cities(db, region_id)
        if not region:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Регион с ID {region_id} не найден"
            )
        return region

    async def get_regions(
            self, db: AsyncSession, skip: int = 0, limit: int = 100
    ) -> Tuple[List[Region], int]:
        """Получить список регионов с пагинацией"""
        regions = await self.region_repository.get_multi(db, skip=skip, limit=limit)
        total = await self.region_repository.get_count(db)
        return regions, total

    async def search_regions(
            self, db: AsyncSession, keyword: str, skip: int = 0, limit: int = 100
    ) -> Tuple[List[Region], int]:
        """Поиск регионов по ключевому слову"""
        regions = await self.region_repository.search(db, keyword=keyword, skip=skip, limit=limit)
        # Для получения общего числа совпадений используем отдельный запрос
        query = self.region_repository.model.__table__.select().where(
            func.lower(self.region_repository.model.name).contains(func.lower(keyword))
        )
        total = await self.region_repository.get_count(db, query)
        return regions, total

    async def create_region(self, db: AsyncSession, region_in: RegionCreate) -> Region:
        """Создать новый регион"""
        # Проверяем, существует ли регион с таким названием
        existing_region = await self.region_repository.get_by_name(db, region_in.name)
        if existing_region:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Регион с названием '{region_in.name}' уже существует"
            )

        return await self.region_repository.create(db, obj_in=region_in)

    async def update_region(
            self, db: AsyncSession, region_id: int, region_in: RegionUpdate
    ) -> Region:
        """Обновить существующий регион"""
        region = await self.get_region(db, region_id)

        # Если обновляется название, проверяем уникальность
        if region_in.name and region_in.name != region.name:
            existing_region = await self.region_repository.get_by_name(db, region_in.name)
            if existing_region:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Регион с названием '{region_in.name}' уже существует"
                )

        return await self.region_repository.update(db, db_obj=region, obj_in=region_in)

    async def delete_region(self, db: AsyncSession, region_id: int) -> Region:
        """Удалить регион по ID"""
        region = await self.get_region(db, region_id)
        return await self.region_repository.remove(db, id=region_id)

    # -- Операции с городами --

    async def get_city(self, db: AsyncSession, city_id: int) -> City:
        """Получить город по ID"""
        city = await self.city_repository.get(db, city_id)
        if not city:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Город с ID {city_id} не найден"
            )
        return city

    async def get_city_with_region(self, db: AsyncSession, city_id: int) -> City:
        """Получить город с информацией о регионе"""
        city = await self.city_repository.get_with_region(db, city_id)
        if not city:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Город с ID {city_id} не найден"
            )
        return city

    async def get_cities(
            self, db: AsyncSession, skip: int = 0, limit: int = 100
    ) -> Tuple[List[City], int]:
        """Получить список городов с пагинацией"""
        cities = await self.city_repository.get_multi(db, skip=skip, limit=limit)
        total = await self.city_repository.get_count(db)
        return cities, total

    async def get_cities_by_region(
            self, db: AsyncSession, region_id: int, skip: int = 0, limit: int = 100
    ) -> Tuple[List[City], int]:
        """Получить города по ID региона"""
        # Проверяем, существует ли регион
        region = await self.region_repository.get(db, region_id)
        if not region:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Регион с ID {region_id} не найден"
            )

        cities = await self.city_repository.get_by_region_id(db, region_id=region_id, skip=skip, limit=limit)
        # Получаем общее число городов для этого региона
        from sqlalchemy import select, func
        query = select(func.count()).where(
            self.city_repository.model.region_id == region_id
        ).select_from(self.city_repository.model)

        result = await db.execute(query)
        total = result.scalar_one()

        return cities, total

    async def search_cities(
            self, db: AsyncSession, keyword: str, region_id: Optional[int] = None, skip: int = 0, limit: int = 100
    ) -> Tuple[List[City], int]:
        """Поиск городов по ключевому слову и опционально по региону"""
        cities = await self.city_repository.search(
            db, keyword=keyword, region_id=region_id, skip=skip, limit=limit
        )

        # Формируем условие для подсчета общего числа совпадений
        from sqlalchemy import or_, func
        conditions = [func.lower(self.city_repository.model.name).contains(func.lower(keyword))]

        if region_id is not None:
            conditions.append(self.city_repository.model.region_id == region_id)

        from sqlalchemy import select
        query = select(func.count()).where(
            or_(*conditions)
        ).select_from(self.city_repository.model)

        result = await db.execute(query)
        total = result.scalar_one()

        return cities, total

    async def create_city(self, db: AsyncSession, city_in: CityCreate) -> City:
        """Создать новый город"""
        # Проверяем, существует ли регион
        region = await self.region_repository.get(db, city_in.region_id)
        if not region:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Регион с ID {city_in.region_id} не найден"
            )

        # Проверяем, не существует ли город с таким названием в этом регионе
        existing_city = await self.city_repository.get_by_name_and_region(
            db, name=city_in.name, region_id=city_in.region_id
        )

        if existing_city:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Город с названием '{city_in.name}' уже существует в этом регионе"
            )

        return await self.city_repository.create(db, obj_in=city_in)

    async def update_city(
            self, db: AsyncSession, city_id: int, city_in: CityUpdate
    ) -> City:
        """Обновить существующий город"""
        city = await self.get_city(db, city_id)

        # Если обновляется ID региона, проверяем его существование
        if city_in.region_id and city_in.region_id != city.region_id:
            region = await self.region_repository.get(db, city_in.region_id)
            if not region:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Регион с ID {city_in.region_id} не найден"
                )

            # Проверяем, не существует ли город с таким названием в новом регионе
            if city_in.name:
                name = city_in.name
            else:
                name = city.name

            existing_city = await self.city_repository.get_by_name_and_region(
                db, name=name, region_id=city_in.region_id
            )

            if existing_city and existing_city.id != city_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Город с названием '{name}' уже существует в регионе с ID {city_in.region_id}"
                )

        # Если обновляется название, проверяем уникальность в текущем регионе
        elif city_in.name and city_in.name != city.name:
            existing_city = await self.city_repository.get_by_name_and_region(
                db, name=city_in.name, region_id=city.region_id
            )

            if existing_city and existing_city.id != city_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Город с названием '{city_in.name}' уже существует в этом регионе"
                )

        return await self.city_repository.update(db, db_obj=city, obj_in=city_in)

    async def delete_city(self, db: AsyncSession, city_id: int) -> City:
        """Удалить город по ID"""
        city = await self.get_city(db, city_id)
        return await self.city_repository.remove(db, id=city_id)

    async def get_largest_cities(
            self, db: AsyncSession, limit: int = 10
    ) -> List[City]:
        """Получить города с наибольшей численностью населения"""
        return await self.city_repository.get_largest_cities(db, limit=limit)


# Экспортируем экземпляр сервиса для использования в API
location_service = LocationService()