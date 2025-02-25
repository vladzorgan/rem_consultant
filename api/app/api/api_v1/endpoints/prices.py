from typing import Any, List, Optional, Dict
from fastapi import APIRouter, Depends, Query, Path, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_async_db
from app.services.price_service import price_service
from app.schemas.repair import (
    ModelRepair, ModelRepairCreate, ModelRepairUpdate, ModelRepairPagination,
    RepairPrice, RepairPriceCreate, RepairPriceUpdate, RepairPricePagination,
    Price, PriceCreate, PriceUpdate, PricePagination
)
from app.core.config import settings

router = APIRouter()


# Эндпоинты для связи модель-тип ремонта (ModelRepair)
@router.get("/model-repairs/by-model/{model_id}", response_model=ModelRepairPagination)
async def read_model_repairs_by_model(
        model_id: int = Path(..., description="ID модели устройства"),
        db: AsyncSession = Depends(get_async_db),
        skip: int = Query(0, description="Количество пропускаемых записей"),
        limit: int = Query(settings.DEFAULT_PAGINATION_LIMIT, description="Максимальное количество записей"),
) -> Any:
    """
    Получить типы ремонта для модели устройства.
    """
    model_repairs, total = await price_service.get_model_repairs_by_model(
        db, model_id=model_id, skip=skip, limit=limit
    )

    # Вычисляем общее количество страниц
    pages = (total + limit - 1) // limit if limit > 0 else 0

    return {
        "items": model_repairs,
        "total": total,
        "page": skip // limit + 1 if limit > 0 else 1,
        "size": limit,
        "pages": pages
    }


@router.get("/model-repairs/by-repair-type/{repair_type_id}", response_model=ModelRepairPagination)
async def read_model_repairs_by_repair_type(
        repair_type_id: int = Path(..., description="ID типа ремонта"),
        db: AsyncSession = Depends(get_async_db),
        skip: int = Query(0, description="Количество пропускаемых записей"),
        limit: int = Query(settings.DEFAULT_PAGINATION_LIMIT, description="Максимальное количество записей"),
) -> Any:
    """
    Получить модели для типа ремонта.
    """
    model_repairs, total = await price_service.get_model_repairs_by_repair_type(
        db, repair_type_id=repair_type_id, skip=skip, limit=limit
    )

    # Вычисляем общее количество страниц
    pages = (total + limit - 1) // limit if limit > 0 else 0

    return {
        "items": model_repairs,
        "total": total,
        "page": skip // limit + 1 if limit > 0 else 1,
        "size": limit,
        "pages": pages
    }


@router.post("/model-repairs/", response_model=ModelRepair, status_code=status.HTTP_201_CREATED)
async def create_model_repair(
        model_repair_in: ModelRepairCreate,
        db: AsyncSession = Depends(get_async_db),
) -> Any:
    """
    Добавить тип ремонта к модели устройства.
    """
    return await price_service.create_model_repair(db, model_repair_in=model_repair_in)


@router.get("/model-repairs/{model_repair_id}", response_model=ModelRepair)
async def read_model_repair(
        model_repair_id: int = Path(..., description="ID связи модель-тип ремонта"),
        db: AsyncSession = Depends(get_async_db),
) -> Any:
    """
    Получить информацию о связи модель-тип ремонта по ID.
    """
    return await price_service.get_model_repair_with_relations(db, model_repair_id=model_repair_id)


@router.put("/model-repairs/{model_repair_id}", response_model=ModelRepair)
async def update_model_repair(
        model_repair_id: int = Path(..., description="ID связи модель-тип ремонта"),
        model_repair_in: ModelRepairUpdate = None,
        db: AsyncSession = Depends(get_async_db),
) -> Any:
    """
    Обновить связь модель-тип ремонта.
    """
    return await price_service.update_model_repair(db, model_repair_id=model_repair_id, model_repair_in=model_repair_in)


@router.delete("/model-repairs/{model_repair_id}", response_model=ModelRepair)
async def delete_model_repair(
        model_repair_id: int = Path(..., description="ID связи модель-тип ремонта"),
        db: AsyncSession = Depends(get_async_db),
) -> Any:
    """
    Удалить связь модель-тип ремонта.
    """
    return await price_service.delete_model_repair(db, model_repair_id=model_repair_id)


# Эндпоинты для стандартных цен на ремонт (RepairPrice)
@router.get("/repair-prices/by-model/{device_model_id}", response_model=RepairPricePagination)
async def read_repair_prices_by_model(
        device_model_id: int = Path(..., description="ID модели устройства"),
        db: AsyncSession = Depends(get_async_db),
        skip: int = Query(0, description="Количество пропускаемых записей"),
        limit: int = Query(settings.DEFAULT_PAGINATION_LIMIT, description="Максимальное количество записей"),
) -> Any:
    """
    Получить цены на ремонт для модели устройства.
    """
    repair_prices, total = await price_service.get_repair_prices_by_model(
        db, device_model_id=device_model_id, skip=skip, limit=limit
    )

    # Вычисляем общее количество страниц
    pages = (total + limit - 1) // limit if limit > 0 else 0

    return {
        "items": repair_prices,
        "total": total,
        "page": skip // limit + 1 if limit > 0 else 1,
        "size": limit,
        "pages": pages
    }


@router.get("/repair-prices/by-repair/{repair_id}", response_model=RepairPricePagination)
async def read_repair_prices_by_repair(
        repair_id: int = Path(..., description="ID ремонта"),
        db: AsyncSession = Depends(get_async_db),
        skip: int = Query(0, description="Количество пропускаемых записей"),
        limit: int = Query(settings.DEFAULT_PAGINATION_LIMIT, description="Максимальное количество записей"),
) -> Any:
    """
    Получить цены на ремонт для типа ремонта.
    """
    repair_prices, total = await price_service.get_repair_prices_by_repair(
        db, repair_id=repair_id, skip=skip, limit=limit
    )

    # Вычисляем общее количество страниц
    pages = (total + limit - 1) // limit if limit > 0 else 0

    return {
        "items": repair_prices,
        "total": total,
        "page": skip // limit + 1 if limit > 0 else 1,
        "size": limit,
        "pages": pages
    }


@router.get("/repair-prices/statistics/", response_model=Dict[str, Any])
async def get_repair_price_statistics(
        repair_id: Optional[int] = Query(None, description="ID ремонта (опционально)"),
        device_model_id: Optional[int] = Query(None, description="ID модели устройства (опционально)"),
        db: AsyncSession = Depends(get_async_db),
) -> Any:
    """
    Получить статистику цен на ремонт.
    """
    return await price_service.get_repair_price_statistics(
        db, repair_id=repair_id, device_model_id=device_model_id
    )


@router.post("/repair-prices/", response_model=RepairPrice, status_code=status.HTTP_201_CREATED)
async def create_repair_price(
        repair_price_in: RepairPriceCreate,
        db: AsyncSession = Depends(get_async_db),
) -> Any:
    """
    Создать новую цену на ремонт.
    """
    return await price_service.create_repair_price(db, repair_price_in=repair_price_in)


@router.get("/repair-prices/{repair_price_id}", response_model=RepairPrice)
async def read_repair_price(
        repair_price_id: int = Path(..., description="ID цены на ремонт"),
        db: AsyncSession = Depends(get_async_db),
) -> Any:
    """
    Получить информацию о цене на ремонт по ID.
    """
    return await price_service.get_repair_price_with_relations(db, repair_price_id=repair_price_id)


@router.put("/repair-prices/{repair_price_id}", response_model=RepairPrice)
async def update_repair_price(
        repair_price_id: int = Path(..., description="ID цены на ремонт"),
        repair_price_in: RepairPriceUpdate = None,
        db: AsyncSession = Depends(get_async_db),
) -> Any:
    """
    Обновить цену на ремонт.
    """
    return await price_service.update_repair_price(
        db, repair_price_id=repair_price_id, repair_price_in=repair_price_in
    )


@router.delete("/repair-prices/{repair_price_id}", response_model=RepairPrice)
async def delete_repair_price(
        repair_price_id: int = Path(..., description="ID цены на ремонт"),
        db: AsyncSession = Depends(get_async_db),
) -> Any:
    """
    Удалить цену на ремонт.
    """
    return await price_service.delete_repair_price(db, repair_price_id=repair_price_id)


# Эндпоинты для цен в сервисных центрах (Price)
@router.get("/prices/by-service-center/{service_center_id}", response_model=PricePagination)
async def read_prices_by_service_center(
        service_center_id: int = Path(..., description="ID сервисного центра"),
        db: AsyncSession = Depends(get_async_db),
        skip: int = Query(0, description="Количество пропускаемых записей"),
        limit: int = Query(settings.DEFAULT_PAGINATION_LIMIT, description="Максимальное количество записей"),
) -> Any:
    """
    Получить все цены для сервисного центра.
    """
    prices, total = await price_service.get_prices_by_service_center(
        db, service_center_id=service_center_id, skip=skip, limit=limit
    )

    # Вычисляем общее количество страниц
    pages = (total + limit - 1) // limit if limit > 0 else 0

    return {
        "items": prices,
        "total": total,
        "page": skip // limit + 1 if limit > 0 else 1,
        "size": limit,
        "pages": pages
    }


@router.get("/prices/by-model-and-repair/", response_model=PricePagination)
async def read_prices_by_model_and_repair(
        device_model_id: int = Query(..., description="ID модели устройства"),
        repair_id: int = Query(..., description="ID ремонта"),
        db: AsyncSession = Depends(get_async_db),
        skip: int = Query(0, description="Количество пропускаемых записей"),
        limit: int = Query(settings.DEFAULT_PAGINATION_LIMIT, description="Максимальное количество записей"),
) -> Any:
    """
    Получить все цены для конкретной модели и типа ремонта.
    """
    prices, total = await price_service.get_prices_by_model_and_repair(
        db, device_model_id=device_model_id, repair_id=repair_id, skip=skip, limit=limit
    )

    # Вычисляем общее количество страниц
    pages = (total + limit - 1) // limit if limit > 0 else 0

    return {
        "items": prices,
        "total": total,
        "page": skip // limit + 1 if limit > 0 else 1,
        "size": limit,
        "pages": pages
    }


@router.get("/prices/comparison/", response_model=Dict[str, Any])
async def get_price_comparison(
        device_model_id: int = Query(..., description="ID модели устройства"),
        repair_id: int = Query(..., description="ID ремонта"),
        db: AsyncSession = Depends(get_async_db),
) -> Any:
    """
    Получить сравнение цен на ремонт по всем сервисным центрам.
    """
    return await price_service.get_price_comparison(
        db, device_model_id=device_model_id, repair_id=repair_id
    )


@router.post("/prices/", response_model=Price, status_code=status.HTTP_201_CREATED)
async def create_price(
        price_in: PriceCreate,
        db: AsyncSession = Depends(get_async_db),
) -> Any:
    """
    Создать новую цену для сервисного центра.
    """
    return await price_service.create_price(db, price_in=price_in)


@router.get("/prices/{price_id}", response_model=Price)
async def read_price(
        price_id: int = Path(..., description="ID цены"),
        db: AsyncSession = Depends(get_async_db),
) -> Any:
    """
    Получить информацию о цене по ID.
    """
    return await price_service.get_price_with_relations(db, price_id=price_id)


@router.put("/prices/{price_id}", response_model=Price)
async def update_price(
        price_id: int = Path(..., description="ID цены"),
        price_in: PriceUpdate = None,
        db: AsyncSession = Depends(get_async_db),
) -> Any:
    """
    Обновить цену.
    """
    return await price_service.update_price(db, price_id=price_id, price_in=price_in)


@router.delete("/prices/{price_id}", response_model=Price)
async def delete_price(
        price_id: int = Path(..., description="ID цены"),
        db: AsyncSession = Depends(get_async_db),
) -> Any:
    """
    Удалить цену.
    """
    return await price_service.delete_price(db, price_id=price_id)