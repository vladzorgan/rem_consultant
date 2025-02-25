from typing import Any, List, Optional
from fastapi import APIRouter, Depends, Query, Path, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_async_db
from app.services.repair_service import repair_service
from app.services.part_service import part_service
from app.schemas.repair import (
    Repair, RepairCreate, RepairUpdate, RepairPagination,
    RepairType, RepairTypeCreate, RepairTypeUpdate, RepairTypePagination,
    Part, PartCreate, PartUpdate, PartPagination,
    RepairPart, RepairPartCreate, RepairPartUpdate
)
from app.core.config import settings

router = APIRouter()


# Эндпоинты для ремонтов (Repair)
@router.get("/", response_model=RepairPagination)
async def read_repairs(
        db: AsyncSession = Depends(get_async_db),
        skip: int = Query(0, description="Количество пропускаемых записей"),
        limit: int = Query(settings.DEFAULT_PAGINATION_LIMIT, description="Максимальное количество записей"),
) -> Any:
    """
    Получить список всех ремонтов с пагинацией.
    """
    repairs, total = await repair_service.get_repairs(db, skip=skip, limit=limit)

    # Вычисляем общее количество страниц
    pages = (total + limit - 1) // limit if limit > 0 else 0

    return {
        "items": repairs,
        "total": total,
        "page": skip // limit + 1 if limit > 0 else 1,
        "size": limit,
        "pages": pages
    }


@router.get("/search/", response_model=RepairPagination)
async def search_repairs(
        keyword: str = Query(..., description="Ключевое слово для поиска"),
        db: AsyncSession = Depends(get_async_db),
        skip: int = Query(0, description="Количество пропускаемых записей"),
        limit: int = Query(settings.DEFAULT_PAGINATION_LIMIT, description="Максимальное количество записей"),
) -> Any:
    """
    Поиск ремонтов по ключевому слову.
    """
    repairs, total = await repair_service.search_repairs(db, keyword=keyword, skip=skip, limit=limit)

    # Вычисляем общее количество страниц
    pages = (total + limit - 1) // limit if limit > 0 else 0

    return {
        "items": repairs,
        "total": total,
        "page": skip // limit + 1 if limit > 0 else 1,
        "size": limit,
        "pages": pages
    }


@router.post("/", response_model=Repair, status_code=status.HTTP_201_CREATED)
async def create_repair(
        repair_in: RepairCreate,
        db: AsyncSession = Depends(get_async_db),
) -> Any:
    """
    Создать новый ремонт.
    """
    return await repair_service.create_repair(db, repair_in=repair_in)


@router.get("/{repair_id}", response_model=Repair)
async def read_repair(
        repair_id: int = Path(..., description="ID ремонта для получения"),
        db: AsyncSession = Depends(get_async_db),
) -> Any:
    """
    Получить информацию о ремонте по его ID.
    """
    return await repair_service.get_repair(db, repair_id=repair_id)


@router.get("/{repair_id}/with-types", response_model=Repair)
async def read_repair_with_types(
        repair_id: int = Path(..., description="ID ремонта для получения"),
        db: AsyncSession = Depends(get_async_db),
) -> Any:
    """
    Получить информацию о ремонте по его ID, включая все его типы.
    """
    return await repair_service.get_repair_with_types(db, repair_id=repair_id)


@router.put("/{repair_id}", response_model=Repair)
async def update_repair(
        repair_id: int = Path(..., description="ID ремонта для обновления"),
        repair_in: RepairUpdate = None,
        db: AsyncSession = Depends(get_async_db),
) -> Any:
    """
    Обновить информацию о ремонте по его ID.
    """
    return await repair_service.update_repair(db, repair_id=repair_id, repair_in=repair_in)


@router.delete("/{repair_id}", response_model=Repair)
async def delete_repair(
        repair_id: int = Path(..., description="ID ремонта для удаления"),
        db: AsyncSession = Depends(get_async_db),
) -> Any:
    """
    Удалить ремонт по его ID.
    """
    return await repair_service.delete_repair(db, repair_id=repair_id)


# Эндпоинты для типов ремонтов (RepairType)
@router.get("/types/", response_model=RepairTypePagination)
async def read_repair_types(
        db: AsyncSession = Depends(get_async_db),
        skip: int = Query(0, description="Количество пропускаемых записей"),
        limit: int = Query(settings.DEFAULT_PAGINATION_LIMIT, description="Максимальное количество записей"),
) -> Any:
    """
    Получить список всех типов ремонтов с пагинацией.
    """
    repair_types, total = await repair_service.get_repair_types(db, skip=skip, limit=limit)

    # Вычисляем общее количество страниц
    pages = (total + limit - 1) // limit if limit > 0 else 0

    return {
        "items": repair_types,
        "total": total,
        "page": skip // limit + 1 if limit > 0 else 1,
        "size": limit,
        "pages": pages
    }


@router.get("/types/by-group/{group_name}", response_model=RepairTypePagination)
async def read_repair_types_by_group(
        group_name: str = Path(..., description="Название группы"),
        db: AsyncSession = Depends(get_async_db),
        skip: int = Query(0, description="Количество пропускаемых записей"),
        limit: int = Query(settings.DEFAULT_PAGINATION_LIMIT, description="Максимальное количество записей"),
) -> Any:
    """
    Получить типы ремонтов по группе.
    """
    repair_types, total = await repair_service.get_repair_types_by_group(
        db, group_name=group_name, skip=skip, limit=limit
    )

    # Вычисляем общее количество страниц
    pages = (total + limit - 1) // limit if limit > 0 else 0

    return {
        "items": repair_types,
        "total": total,
        "page": skip // limit + 1 if limit > 0 else 1,
        "size": limit,
        "pages": pages
    }


@router.get("/types/search/", response_model=RepairTypePagination)
async def search_repair_types(
        keyword: str = Query(..., description="Ключевое слово для поиска"),
        group_name: Optional[str] = Query(None, description="Название группы (опционально)"),
        db: AsyncSession = Depends(get_async_db),
        skip: int = Query(0, description="Количество пропускаемых записей"),
        limit: int = Query(settings.DEFAULT_PAGINATION_LIMIT, description="Максимальное количество записей"),
) -> Any:
    """
    Поиск типов ремонтов по ключевому слову и опционально по группе.
    """
    repair_types, total = await repair_service.search_repair_types(
        db, keyword=keyword, group_name=group_name, skip=skip, limit=limit
    )

    # Вычисляем общее количество страниц
    pages = (total + limit - 1) // limit if limit > 0 else 0

    return {
        "items": repair_types,
        "total": total,
        "page": skip // limit + 1 if limit > 0 else 1,
        "size": limit,
        "pages": pages
    }


@router.post("/types/", response_model=RepairType, status_code=status.HTTP_201_CREATED)
async def create_repair_type(
        repair_type_in: RepairTypeCreate,
        db: AsyncSession = Depends(get_async_db),
) -> Any:
    """
    Создать новый тип ремонта.
    """
    return await repair_service.create_repair_type(db, repair_type_in=repair_type_in)


@router.get("/types/{repair_type_id}", response_model=RepairType)
async def read_repair_type(
        repair_type_id: int = Path(..., description="ID типа ремонта для получения"),
        db: AsyncSession = Depends(get_async_db),
) -> Any:
    """
    Получить информацию о типе ремонта по его ID.
    """
    return await repair_service.get_repair_type(db, repair_type_id=repair_type_id)


@router.get("/types/{repair_type_id}/with-parts", response_model=RepairType)
async def read_repair_type_with_parts(
        repair_type_id: int = Path(..., description="ID типа ремонта для получения"),
        db: AsyncSession = Depends(get_async_db),
) -> Any:
    """
    Получить информацию о типе ремонта по его ID, включая все его запчасти.
    """
    return await repair_service.get_repair_type_with_parts(db, repair_type_id=repair_type_id)


@router.put("/types/{repair_type_id}", response_model=RepairType)
async def update_repair_type(
        repair_type_id: int = Path(..., description="ID типа ремонта для обновления"),
        repair_type_in: RepairTypeUpdate = None,
        db: AsyncSession = Depends(get_async_db),
) -> Any:
    """
    Обновить информацию о типе ремонта по его ID.
    """
    return await repair_service.update_repair_type(db, repair_type_id=repair_type_id, repair_type_in=repair_type_in)


@router.delete("/types/{repair_type_id}", response_model=RepairType)
async def delete_repair_type(
        repair_type_id: int = Path(..., description="ID типа ремонта для удаления"),
        db: AsyncSession = Depends(get_async_db),
) -> Any:
    """
    Удалить тип ремонта по его ID.
    """
    return await repair_service.delete_repair_type(db, repair_type_id=repair_type_id)


# Эндпоинты для запчастей (Part)
@router.get("/parts/", response_model=PartPagination)
async def read_parts(
        db: AsyncSession = Depends(get_async_db),
        skip: int = Query(0, description="Количество пропускаемых записей"),
        limit: int = Query(settings.DEFAULT_PAGINATION_LIMIT, description="Максимальное количество записей"),
) -> Any:
    """
    Получить список всех запчастей с пагинацией.
    """
    parts, total = await part_service.get_parts(db, skip=skip, limit=limit)

    # Вычисляем общее количество страниц
    pages = (total + limit - 1) // limit if limit > 0 else 0

    return {
        "items": parts,
        "total": total,
        "page": skip // limit + 1 if limit > 0 else 1,
        "size": limit,
        "pages": pages
    }


@router.get("/parts/by-price-range/", response_model=PartPagination)
async def read_parts_by_price_range(
        min_price: float = Query(0, description="Минимальная цена"),
        max_price: Optional[float] = Query(None, description="Максимальная цена"),
        db: AsyncSession = Depends(get_async_db),
        skip: int = Query(0, description="Количество пропускаемых записей"),
        limit: int = Query(settings.DEFAULT_PAGINATION_LIMIT, description="Максимальное количество записей"),
) -> Any:
    """
    Получить запчасти в заданном диапазоне цен.
    """
    parts, total = await part_service.get_parts_by_price_range(
        db, min_price=min_price, max_price=max_price, skip=skip, limit=limit
    )

    # Вычисляем общее количество страниц
    pages = (total + limit - 1) // limit if limit > 0 else 0

    return {
        "items": parts,
        "total": total,
        "page": skip // limit + 1 if limit > 0 else 1,
        "size": limit,
        "pages": pages
    }


@router.get("/parts/search/", response_model=PartPagination)
async def search_parts(
        keyword: str = Query(..., description="Ключевое слово для поиска"),
        db: AsyncSession = Depends(get_async_db),
        skip: int = Query(0, description="Количество пропускаемых записей"),
        limit: int = Query(settings.DEFAULT_PAGINATION_LIMIT, description="Максимальное количество записей"),
) -> Any:
    """
    Поиск запчастей по ключевому слову.
    """
    parts, total = await part_service.search_parts(db, keyword=keyword, skip=skip, limit=limit)

    # Вычисляем общее количество страниц
    pages = (total + limit - 1) // limit if limit > 0 else 0

    return {
        "items": parts,
        "total": total,
        "page": skip // limit + 1 if limit > 0 else 1,
        "size": limit,
        "pages": pages
    }


@router.post("/parts/", response_model=Part, status_code=status.HTTP_201_CREATED)
async def create_part(
        part_in: PartCreate,
        db: AsyncSession = Depends(get_async_db),
) -> Any:
    """
    Создать новую запчасть.
    """
    return await part_service.create_part(db, part_in=part_in)


@router.get("/parts/{part_id}", response_model=Part)
async def read_part(
        part_id: int = Path(..., description="ID запчасти для получения"),
        db: AsyncSession = Depends(get_async_db),
) -> Any:
    """
    Получить информацию о запчасти по ее ID.
    """
    return await part_service.get_part(db, part_id=part_id)


@router.get("/parts/by-sku/{sku}", response_model=Part)
async def read_part_by_sku(
        sku: str = Path(..., description="Артикул (SKU) запчасти"),
        db: AsyncSession = Depends(get_async_db),
) -> Any:
    """
    Получить информацию о запчасти по ее артикулу (SKU).
    """
    return await part_service.get_part_by_sku(db, sku=sku)


@router.put("/parts/{part_id}", response_model=Part)
async def update_part(
        part_id: int = Path(..., description="ID запчасти для обновления"),
        part_in: PartUpdate = None,
        db: AsyncSession = Depends(get_async_db),
) -> Any:
    """
    Обновить информацию о запчасти по ее ID.
    """
    return await part_service.update_part(db, part_id=part_id, part_in=part_in)


@router.delete("/parts/{part_id}", response_model=Part)
async def delete_part(
        part_id: int = Path(..., description="ID запчасти для удаления"),
        db: AsyncSession = Depends(get_async_db),
) -> Any:
    """
    Удалить запчасть по ее ID.
    """
    return await part_service.delete_part(db, part_id=part_id)


# Эндпоинты для связи ремонт-запчасть (RepairPart)
@router.get("/types/{repair_type_id}/parts/", response_model=List[RepairPart])
async def read_repair_parts_by_repair_type(
        repair_type_id: int = Path(..., description="ID типа ремонта"),
        db: AsyncSession = Depends(get_async_db),
        skip: int = Query(0, description="Количество пропускаемых записей"),
        limit: int = Query(settings.DEFAULT_PAGINATION_LIMIT, description="Максимальное количество записей"),
) -> Any:
    """
    Получить запчасти для типа ремонта.
    """
    repair_parts, _ = await part_service.get_repair_parts_by_repair_type(
        db, repair_type_id=repair_type_id, skip=skip, limit=limit
    )
    return repair_parts


@router.post("/types/{repair_type_id}/parts/", response_model=RepairPart, status_code=status.HTTP_201_CREATED)
async def create_repair_part(
        repair_type_id: int = Path(..., description="ID типа ремонта"),
        repair_part_in: RepairPartCreate = None,
        db: AsyncSession = Depends(get_async_db),
) -> Any:
    """
    Добавить запчасть к типу ремонта.
    """
    # Убедимся, что repair_type_id в пути и в теле запроса совпадают
    if repair_part_in.repair_type_id != repair_type_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID типа ремонта в пути и теле запроса не совпадают"
        )

    return await part_service.create_repair_part(db, repair_part_in=repair_part_in)


@router.get("/repair-parts/{repair_part_id}", response_model=RepairPart)
async def read_repair_part(
        repair_part_id: int = Path(..., description="ID связи ремонт-запчасть"),
        db: AsyncSession = Depends(get_async_db),
) -> Any:
    """
    Получить информацию о связи ремонт-запчасть по ID.
    """
    return await part_service.get_repair_part_with_part(db, repair_part_id=repair_part_id)


@router.put("/repair-parts/{repair_part_id}", response_model=RepairPart)
async def update_repair_part(
        repair_part_id: int = Path(..., description="ID связи ремонт-запчасть"),
        repair_part_in: RepairPartUpdate = None,
        db: AsyncSession = Depends(get_async_db),
) -> Any:
    """
    Обновить связь ремонт-запчасть.
    """
    return await part_service.update_repair_part(db, repair_part_id=repair_part_id, repair_part_in=repair_part_in)


@router.delete("/repair-parts/{repair_part_id}", response_model=RepairPart)
async def delete_repair_part(
        repair_part_id: int = Path(..., description="ID связи ремонт-запчасть"),
        db: AsyncSession = Depends(get_async_db),
) -> Any:
    """
    Удалить связь ремонт-запчасть.
    """
    return await part_service.delete_repair_part(db, repair_part_id=repair_part_id)