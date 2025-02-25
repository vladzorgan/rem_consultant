from typing import Any, List, Optional
from fastapi import APIRouter, Depends, Query, Path, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_async_db
from app.services.device_service import device_service
from app.schemas.device import (
    DeviceBrand, DeviceBrandCreate, DeviceBrandUpdate, DeviceBrandWithModels, DeviceBrandPagination,
    DeviceModel, DeviceModelCreate, DeviceModelUpdate, DeviceModelPagination
)
from app.core.config import settings

router = APIRouter()


# Эндпоинты для брендов устройств

@router.get("/brands/", response_model=DeviceBrandPagination)
async def read_brands(
        db: AsyncSession = Depends(get_async_db),
        skip: int = Query(0, description="Количество пропускаемых записей"),
        limit: int = Query(settings.DEFAULT_PAGINATION_LIMIT, description="Максимальное количество записей"),
) -> Any:
    """
    Получить список всех брендов устройств с пагинацией.
    """
    brands, total = await device_service.get_brands(db, skip=skip, limit=limit)

    # Вычисляем общее количество страниц
    pages = (total + limit - 1) // limit if limit > 0 else 0

    return {
        "items": brands,
        "total": total,
        "page": skip // limit + 1 if limit > 0 else 1,
        "size": limit,
        "pages": pages
    }


@router.get("/brands/search/", response_model=DeviceBrandPagination)
async def search_brands(
        keyword: str = Query(..., description="Ключевое слово для поиска"),
        db: AsyncSession = Depends(get_async_db),
        skip: int = Query(0, description="Количество пропускаемых записей"),
        limit: int = Query(settings.DEFAULT_PAGINATION_LIMIT, description="Максимальное количество записей"),
) -> Any:
    """
    Поиск брендов устройств по ключевому слову.
    """
    brands, total = await device_service.search_brands(db, keyword=keyword, skip=skip, limit=limit)

    # Вычисляем общее количество страниц
    pages = (total + limit - 1) // limit if limit > 0 else 0

    return {
        "items": brands,
        "total": total,
        "page": skip // limit + 1 if limit > 0 else 1,
        "size": limit,
        "pages": pages
    }


@router.post("/brands/", response_model=DeviceBrand, status_code=status.HTTP_201_CREATED)
async def create_brand(
        brand_in: DeviceBrandCreate,
        db: AsyncSession = Depends(get_async_db),
) -> Any:
    """
    Создать новый бренд устройства.
    """
    return await device_service.create_brand(db, brand_in=brand_in)


@router.get("/brands/{brand_id}", response_model=DeviceBrand)
async def read_brand(
        brand_id: int = Path(..., description="ID бренда для получения"),
        db: AsyncSession = Depends(get_async_db),
) -> Any:
    """
    Получить информацию о бренде по его ID.
    """
    return await device_service.get_brand(db, brand_id=brand_id)


@router.get("/brands/{brand_id}/with-models", response_model=DeviceBrandWithModels)
async def read_brand_with_models(
        brand_id: int = Path(..., description="ID бренда для получения"),
        db: AsyncSession = Depends(get_async_db),
) -> Any:
    """
    Получить информацию о бренде по его ID, включая все его модели.
    """
    return await device_service.get_brand_with_models(db, brand_id=brand_id)


@router.put("/brands/{brand_id}", response_model=DeviceBrand)
async def update_brand(
        brand_id: int = Path(..., description="ID бренда для обновления"),
        brand_in: DeviceBrandUpdate = None,
        db: AsyncSession = Depends(get_async_db),
) -> Any:
    """
    Обновить информацию о бренде по его ID.
    """
    return await device_service.update_brand(db, brand_id=brand_id, brand_in=brand_in)


@router.delete("/brands/{brand_id}", response_model=DeviceBrand)
async def delete_brand(
        brand_id: int = Path(..., description="ID бренда для удаления"),
        db: AsyncSession = Depends(get_async_db),
) -> Any:
    """
    Удалить бренд по его ID.
    """
    return await device_service.delete_brand(db, brand_id=brand_id)


# Эндпоинты для моделей устройств

@router.get("/models/", response_model=DeviceModelPagination)
async def read_models(
        db: AsyncSession = Depends(get_async_db),
        skip: int = Query(0, description="Количество пропускаемых записей"),
        limit: int = Query(settings.DEFAULT_PAGINATION_LIMIT, description="Максимальное количество записей"),
) -> Any:
    """
    Получить список всех моделей устройств с пагинацией.
    """
    models, total = await device_service.get_models(db, skip=skip, limit=limit)

    # Вычисляем общее количество страниц
    pages = (total + limit - 1) // limit if limit > 0 else 0

    return {
        "items": models,
        "total": total,
        "page": skip // limit + 1 if limit > 0 else 1,
        "size": limit,
        "pages": pages
    }


@router.get("/brands/{brand_id}/models/", response_model=DeviceModelPagination)
async def read_models_by_brand(
        brand_id: int = Path(..., description="ID бренда для получения моделей"),
        db: AsyncSession = Depends(get_async_db),
        skip: int = Query(0, description="Количество пропускаемых записей"),
        limit: int = Query(settings.DEFAULT_PAGINATION_LIMIT, description="Максимальное количество записей"),
) -> Any:
    """
    Получить список всех моделей для указанного бренда с пагинацией.
    """
    models, total = await device_service.get_models_by_brand(
        db, brand_id=brand_id, skip=skip, limit=limit
    )

    # Вычисляем общее количество страниц
    pages = (total + limit - 1) // limit if limit > 0 else 0

    return {
        "items": models,
        "total": total,
        "page": skip // limit + 1 if limit > 0 else 1,
        "size": limit,
        "pages": pages
    }


@router.get("/models/search/", response_model=DeviceModelPagination)
async def search_models(
        keyword: str = Query(..., description="Ключевое слово для поиска"),
        brand_id: Optional[int] = Query(None, description="ID бренда для фильтрации (опционально)"),
        db: AsyncSession = Depends(get_async_db),
        skip: int = Query(0, description="Количество пропускаемых записей"),
        limit: int = Query(settings.DEFAULT_PAGINATION_LIMIT, description="Максимальное количество записей"),
) -> Any:
    """
    Поиск моделей устройств по ключевому слову с опциональной фильтрацией по бренду.
    """
    models, total = await device_service.search_models(
        db, keyword=keyword, brand_id=brand_id, skip=skip, limit=limit
    )

    # Вычисляем общее количество страниц
    pages = (total + limit - 1) // limit if limit > 0 else 0

    return {
        "items": models,
        "total": total,
        "page": skip // limit + 1 if limit > 0 else 1,
        "size": limit,
        "pages": pages
    }


@router.post("/models/", response_model=DeviceModel, status_code=status.HTTP_201_CREATED)
async def create_model(
        model_in: DeviceModelCreate,
        db: AsyncSession = Depends(get_async_db),
) -> Any:
    """
    Создать новую модель устройства.
    """
    return await device_service.create_model(db, model_in=model_in)


@router.get("/models/{model_id}", response_model=DeviceModel)
async def read_model(
        model_id: int = Path(..., description="ID модели для получения"),
        db: AsyncSession = Depends(get_async_db),
) -> Any:
    """
    Получить информацию о модели по ее ID.
    """
    return await device_service.get_model(db, model_id=model_id)


@router.put("/models/{model_id}", response_model=DeviceModel)
async def update_model(
        model_id: int = Path(..., description="ID модели для обновления"),
        model_in: DeviceModelUpdate = None,
        db: AsyncSession = Depends(get_async_db),
) -> Any:
    """
    Обновить информацию о модели по ее ID.
    """
    return await device_service.update_model(db, model_id=model_id, model_in=model_in)


@router.delete("/models/{model_id}", response_model=DeviceModel)
async def delete_model(
        model_id: int = Path(..., description="ID модели для удаления"),
        db: AsyncSession = Depends(get_async_db),
) -> Any:
    """
    Удалить модель по ее ID.
    """
    return await device_service.delete_model(db, model_id=model_id)