from typing import Any, List, Optional
from fastapi import APIRouter, Depends, Query, Path, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_async_db
from app.services.location_service import location_service
from app.schemas.location import (
    Region, RegionCreate, RegionUpdate, RegionWithCities, RegionPagination,
    City, CityCreate, CityUpdate, CityPagination
)
from app.core.config import settings

router = APIRouter()


# Эндпоинты для регионов

@router.get("/regions/", response_model=RegionPagination)
async def read_regions(
        db: AsyncSession = Depends(get_async_db),
        skip: int = Query(0, description="Количество пропускаемых записей"),
        limit: int = Query(settings.DEFAULT_PAGINATION_LIMIT, description="Максимальное количество записей"),
) -> Any:
    """
    Получить список всех регионов с пагинацией.
    """
    regions, total = await location_service.get_regions(db, skip=skip, limit=limit)

    # Вычисляем общее количество страниц
    pages = (total + limit - 1) // limit if limit > 0 else 0

    return {
        "items": regions,
        "total": total,
        "page": skip // limit + 1 if limit > 0 else 1,
        "size": limit,
        "pages": pages
    }


@router.get("/regions/search/", response_model=RegionPagination)
async def search_regions(
        keyword: str = Query(..., description="Ключевое слово для поиска"),
        db: AsyncSession = Depends(get_async_db),
        skip: int = Query(0, description="Количество пропускаемых записей"),
        limit: int = Query(settings.DEFAULT_PAGINATION_LIMIT, description="Максимальное количество записей"),
) -> Any:
    """
    Поиск регионов по ключевому слову.
    """
    regions, total = await location_service.search_regions(db, keyword=keyword, skip=skip, limit=limit)

    # Вычисляем общее количество страниц
    pages = (total + limit - 1) // limit if limit > 0 else 0

    return {
        "items": regions,
        "total": total,
        "page": skip // limit + 1 if limit > 0 else 1,
        "size": limit,
        "pages": pages
    }


@router.post("/regions/", response_model=Region, status_code=status.HTTP_201_CREATED)
async def create_region(
        region_in: RegionCreate,
        db: AsyncSession = Depends(get_async_db),
) -> Any:
    """
    Создать новый регион.
    """
    return await location_service.create_region(db, region_in=region_in)


@router.get("/regions/{region_id}", response_model=Region)
async def read_region(
        region_id: int = Path(..., description="ID региона для получения"),
        db: AsyncSession = Depends(get_async_db),
) -> Any:
    """
    Получить информацию о регионе по его ID.
    """
    return await location_service.get_region(db, region_id=region_id)


@router.get("/regions/{region_id}/with-cities", response_model=RegionWithCities)
async def read_region_with_cities(
        region_id: int = Path(..., description="ID региона для получения"),
        db: AsyncSession = Depends(get_async_db),
) -> Any:
    """
    Получить информацию о регионе по его ID, включая все его города.
    """
    return await location_service.get_region_with_cities(db, region_id=region_id)


@router.put("/regions/{region_id}", response_model=Region)
async def update_region(
        region_id: int = Path(..., description="ID региона для обновления"),
        region_in: RegionUpdate = None,
        db: AsyncSession = Depends(get_async_db),
) -> Any:
    """
    Обновить информацию о регионе по его ID.
    """
    return await location_service.update_region(db, region_id=region_id, region_in=region_in)


@router.delete("/regions/{region_id}", response_model=Region)
async def delete_region(
        region_id: int = Path(..., description="ID региона для удаления"),
        db: AsyncSession = Depends(get_async_db),
) -> Any:
    """
    Удалить регион по его ID.
    """
    return await location_service.delete_region(db, region_id=region_id)


# Эндпоинты для городов

@router.get("/cities/", response_model=CityPagination)
async def read_cities(
        db: AsyncSession = Depends(get_async_db),
        skip: int = Query(0, description="Количество пропускаемых записей"),
        limit: int = Query(settings.DEFAULT_PAGINATION_LIMIT, description="Максимальное количество записей"),
) -> Any:
    """
    Получить список всех городов с пагинацией.
    """
    cities, total = await location_service.get_cities(db, skip=skip, limit=limit)

    # Вычисляем общее количество страниц
    pages = (total + limit - 1) // limit if limit > 0 else 0

    return {
        "items": cities,
        "total": total,
        "page": skip // limit + 1 if limit > 0 else 1,
        "size": limit,
        "pages": pages
    }


@router.get("/cities/largest/", response_model=List[City])
async def read_largest_cities(
        limit: int = Query(10, description="Количество крупнейших городов для получения"),
        db: AsyncSession = Depends(get_async_db),
) -> Any:
    """
    Получить список крупнейших городов по населению.
    """
    return await location_service.get_largest_cities(db, limit=limit)


@router.get("/regions/{region_id}/cities/", response_model=CityPagination)
async def read_cities_by_region(
        region_id: int = Path(..., description="ID региона для получения городов"),
        db: AsyncSession = Depends(get_async_db),
        skip: int = Query(0, description="Количество пропускаемых записей"),
        limit: int = Query(settings.DEFAULT_PAGINATION_LIMIT, description="Максимальное количество записей"),
) -> Any:
    """
    Получить список всех городов для указанного региона с пагинацией.
    """
    cities, total = await location_service.get_cities_by_region(
        db, region_id=region_id, skip=skip, limit=limit
    )

    # Вычисляем общее количество страниц
    pages = (total + limit - 1) // limit if limit > 0 else 0

    return {
        "items": cities,
        "total": total,
        "page": skip // limit + 1 if limit > 0 else 1,
        "size": limit,
        "pages": pages
    }


@router.get("/cities/search/", response_model=CityPagination)
async def search_cities(
        keyword: str = Query(..., description="Ключевое слово для поиска"),
        region_id: Optional[int] = Query(None, description="ID региона для фильтрации (опционально)"),
        db: AsyncSession = Depends(get_async_db),
        skip: int = Query(0, description="Количество пропускаемых записей"),
        limit: int = Query(settings.DEFAULT_PAGINATION_LIMIT, description="Максимальное количество записей"),
) -> Any:
    """
    Поиск городов по ключевому слову с опциональной фильтрацией по региону.
    """
    cities, total = await location_service.search_cities(
        db, keyword=keyword, region_id=region_id, skip=skip, limit=limit
    )

    # Вычисляем общее количество страниц
    pages = (total + limit - 1) // limit if limit > 0 else 0

    return {
        "items": cities,
        "total": total,
        "page": skip // limit + 1 if limit > 0 else 1,
        "size": limit,
        "pages": pages
    }


@router.post("/cities/", response_model=City, status_code=status.HTTP_201_CREATED)
async def create_city(
        city_in: CityCreate,
        db: AsyncSession = Depends(get_async_db),
) -> Any:
    """
    Создать новый город.
    """
    return await location_service.create_city(db, city_in=city_in)


@router.get("/cities/{city_id}", response_model=City)
async def read_city(
        city_id: int = Path(..., description="ID города для получения"),
        db: AsyncSession = Depends(get_async_db),
) -> Any:
    """
    Получить информацию о городе по его ID.
    """
    return await location_service.get_city_with_region(db, city_id=city_id)


@router.put("/cities/{city_id}", response_model=City)
async def update_city(
        city_id: int = Path(..., description="ID города для обновления"),
        city_in: CityUpdate = None,
        db: AsyncSession = Depends(get_async_db),
) -> Any:
    """
    Обновить информацию о городе по его ID.
    """
    return await location_service.update_city(db, city_id=city_id, city_in=city_in)


@router.delete("/cities/{city_id}", response_model=City)
async def delete_city(
        city_id: int = Path(..., description="ID города для удаления"),
        db: AsyncSession = Depends(get_async_db),
) -> Any:
    """
    Удалить город по его ID.
    """
    return await location_service.delete_city(db, city_id=city_id)