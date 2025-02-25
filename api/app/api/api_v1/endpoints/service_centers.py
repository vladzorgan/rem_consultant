from typing import Any, List, Optional, Dict
from fastapi import APIRouter, Depends, Query, Path, HTTPException, status, Body
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_async_db, get_current_user, get_current_admin_user
from app.services.service_center_service import service_center_service
from app.schemas.service_center import (
    ServiceCenter, ServiceCenterCreate, ServiceCenterUpdate, ServiceCenterDetail, ServiceCenterPagination,
    ServiceCenterAddress, ServiceCenterAddressCreate, ServiceCenterAddressUpdate,
    ServiceCenterLink, ServiceCenterLinkCreate, ServiceCenterLinkUpdate,
    Review, ReviewCreate, ReviewUpdate, ReviewPagination,
    AddServiceRequest, AddServiceRequestCreate, AddServiceRequestUpdate, AddServiceRequestPagination
)
from app.models.user import User
from app.core.config import settings

router = APIRouter()


# Эндпоинты для сервисных центров
@router.get("/", response_model=ServiceCenterPagination)
async def read_service_centers(
        db: AsyncSession = Depends(get_async_db),
        skip: int = Query(0, description="Количество пропускаемых записей"),
        limit: int = Query(settings.DEFAULT_PAGINATION_LIMIT, description="Максимальное количество записей"),
) -> Any:
    """
    Получить список всех сервисных центров с пагинацией.
    """
    service_centers, total = await service_center_service.get_service_centers(db, skip=skip, limit=limit)

    # Вычисляем общее количество страниц
    pages = (total + limit - 1) // limit if limit > 0 else 0

    return {
        "items": service_centers,
        "total": total,
        "page": skip // limit + 1 if limit > 0 else 1,
        "size": limit,
        "pages": pages
    }


@router.get("/search/", response_model=ServiceCenterPagination)
async def search_service_centers(
        keyword: str = Query(..., description="Ключевое слово для поиска"),
        city_id: Optional[int] = Query(None, description="ID города для фильтрации (опционально)"),
        db: AsyncSession = Depends(get_async_db),
        skip: int = Query(0, description="Количество пропускаемых записей"),
        limit: int = Query(settings.DEFAULT_PAGINATION_LIMIT, description="Максимальное количество записей"),
) -> Any:
    """
    Поиск сервисных центров по ключевому слову и опционально по городу.
    """
    service_centers, total = await service_center_service.search_service_centers(
        db, keyword=keyword, city_id=city_id, skip=skip, limit=limit
    )

    # Вычисляем общее количество страниц
    pages = (total + limit - 1) // limit if limit > 0 else 0

    return {
        "items": service_centers,
        "total": total,
        "page": skip // limit + 1 if limit > 0 else 1,
        "size": limit,
        "pages": pages
    }


@router.get("/by-city/{city_id}", response_model=ServiceCenterPagination)
async def read_service_centers_by_city(
        city_id: int = Path(..., description="ID города"),
        db: AsyncSession = Depends(get_async_db),
        skip: int = Query(0, description="Количество пропускаемых записей"),
        limit: int = Query(settings.DEFAULT_PAGINATION_LIMIT, description="Максимальное количество записей"),
) -> Any:
    """
    Получить сервисные центры для указанного города.
    """
    service_centers, total = await service_center_service.get_service_centers_by_city(
        db, city_id=city_id, skip=skip, limit=limit
    )

    # Вычисляем общее количество страниц
    pages = (total + limit - 1) // limit if limit > 0 else 0

    return {
        "items": service_centers,
        "total": total,
        "page": skip // limit + 1 if limit > 0 else 1,
        "size": limit,
        "pages": pages
    }


@router.get("/by-owner/{owner_id}", response_model=ServiceCenterPagination)
async def read_service_centers_by_owner(
        owner_id: int = Path(..., description="ID владельца"),
        db: AsyncSession = Depends(get_async_db),
        skip: int = Query(0, description="Количество пропускаемых записей"),
        limit: int = Query(settings.DEFAULT_PAGINATION_LIMIT, description="Максимальное количество записей"),
) -> Any:
    """
    Получить сервисные центры для указанного владельца.
    """
    service_centers, total = await service_center_service.get_service_centers_by_owner(
        db, owner_id=owner_id, skip=skip, limit=limit
    )

    # Вычисляем общее количество страниц
    pages = (total + limit - 1) // limit if limit > 0 else 0

    return {
        "items": service_centers,
        "total": total,
        "page": skip // limit + 1 if limit > 0 else 1,
        "size": limit,
        "pages": pages
    }


@router.get("/top-rated/", response_model=List[ServiceCenter])
async def read_top_rated_service_centers(
        limit: int = Query(10, description="Количество сервисных центров для получения"),
        db: AsyncSession = Depends(get_async_db),
) -> Any:
    """
    Получить сервисные центры с лучшим рейтингом.
    """
    return await service_center_service.get_top_rated_service_centers(db, limit=limit)


@router.post("/", response_model=ServiceCenter, status_code=status.HTTP_201_CREATED)
async def create_service_center(
        service_center_in: ServiceCenterCreate,
        db: AsyncSession = Depends(get_async_db),
        current_user: User = Depends(get_current_admin_user),
) -> Any:
    """
    Создать новый сервисный центр.
    Требуются права администратора.
    """
    return await service_center_service.create_service_center(db, service_center_in=service_center_in)


@router.get("/{service_center_id}", response_model=ServiceCenter)
async def read_service_center(
        service_center_id: int = Path(..., description="ID сервисного центра для получения"),
        db: AsyncSession = Depends(get_async_db),
) -> Any:
    """
    Получить информацию о сервисном центре по его ID.
    """
    return await service_center_service.get_service_center(db, service_center_id=service_center_id)


@router.get("/{service_center_id}/detail", response_model=ServiceCenterDetail)
async def read_service_center_detail(
        service_center_id: int = Path(..., description="ID сервисного центра для получения"),
        db: AsyncSession = Depends(get_async_db),
) -> Any:
    """
    Получить детальную информацию о сервисном центре по его ID, включая связанные данные.
    """
    return await service_center_service.get_service_center_with_relations(db, service_center_id=service_center_id)


@router.put("/{service_center_id}", response_model=ServiceCenter)
async def update_service_center(
        service_center_id: int = Path(..., description="ID сервисного центра для обновления"),
        service_center_in: ServiceCenterUpdate = None,
        db: AsyncSession = Depends(get_async_db),
        current_user: User = Depends(get_current_user),
) -> Any:
    """
    Обновить информацию о сервисном центре по его ID.
    Пользователь должен быть владельцем сервисного центра или администратором.
    """
    service_center = await service_center_service.get_service_center(db, service_center_id=service_center_id)

    # Проверяем права доступа
    if not current_user.is_admin and (not service_center.owner_id or service_center.owner_id != current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для выполнения операции"
        )

    return await service_center_service.update_service_center(
        db, service_center_id=service_center_id, service_center_in=service_center_in
    )


@router.delete("/{service_center_id}", response_model=ServiceCenter)
async def delete_service_center(
        service_center_id: int = Path(..., description="ID сервисного центра для удаления"),
        db: AsyncSession = Depends(get_async_db),
        current_user: User = Depends(get_current_admin_user),
) -> Any:
    """
    Удалить сервисный центр по его ID.
    Требуются права администратора.
    """
    return await service_center_service.delete_service_center(db, service_center_id=service_center_id)


# Эндпоинты для адресов сервисных центров
@router.get("/{service_center_id}/addresses/", response_model=List[ServiceCenterAddress])
async def read_service_center_addresses(
        service_center_id: int = Path(..., description="ID сервисного центра"),
        db: AsyncSession = Depends(get_async_db),
        skip: int = Query(0, description="Количество пропускаемых записей"),
        limit: int = Query(settings.DEFAULT_PAGINATION_LIMIT, description="Максимальное количество записей"),
) -> Any:
    """
    Получить адреса для сервисного центра.
    """
    addresses, _ = await service_center_service.get_addresses_by_service_center(
        db, service_center_id=service_center_id, skip=skip, limit=limit
    )
    return addresses


@router.post("/{service_center_id}/addresses/", response_model=ServiceCenterAddress,
             status_code=status.HTTP_201_CREATED)
async def create_service_center_address(
        service_center_id: int = Path(..., description="ID сервисного центра"),
        address_in: ServiceCenterAddressCreate = None,
        db: AsyncSession = Depends(get_async_db),
        current_user: User = Depends(get_current_user),
) -> Any:
    """
    Добавить адрес для сервисного центра.
    Пользователь должен быть владельцем сервисного центра или администратором.
    """
    service_center = await service_center_service.get_service_center(db, service_center_id=service_center_id)

    # Проверяем права доступа
    if not current_user.is_admin and (not service_center.owner_id or service_center.owner_id != current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для выполнения операции"
        )

    # Убедимся, что service_center_id в пути и в теле запроса совпадают
    if address_in.service_center_id != service_center_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID сервисного центра в пути и теле запроса не совпадают"
        )

    return await service_center_service.create_address(db, address_in=address_in)


@router.get("/addresses/{address_id}", response_model=ServiceCenterAddress)
async def read_service_center_address(
        address_id: int = Path(..., description="ID адреса"),
        db: AsyncSession = Depends(get_async_db),
) -> Any:
    """
    Получить информацию об адресе по его ID.
    """
    return await service_center_service.get_address(db, address_id=address_id)


@router.put("/addresses/{address_id}", response_model=ServiceCenterAddress)
async def update_service_center_address(
        address_id: int = Path(..., description="ID адреса для обновления"),
        address_in: ServiceCenterAddressUpdate = None,
        db: AsyncSession = Depends(get_async_db),
        current_user: User = Depends(get_current_user),
) -> Any:
    """
    Обновить адрес по его ID.
    Пользователь должен быть владельцем сервисного центра или администратором.
    """
    address = await service_center_service.get_address(db, address_id=address_id)
    service_center = await service_center_service.get_service_center(db, service_center_id=address.service_center_id)

    # Проверяем права доступа
    if not current_user.is_admin and (not service_center.owner_id or service_center.owner_id != current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для выполнения операции"
        )

    return await service_center_service.update_address(db, address_id=address_id, address_in=address_in)


@router.delete("/addresses/{address_id}", response_model=ServiceCenterAddress)
async def delete_service_center_address(
        address_id: int = Path(..., description="ID адреса для удаления"),
        db: AsyncSession = Depends(get_async_db),
        current_user: User = Depends(get_current_user),
) -> Any:
    """
    Удалить адрес по его ID.
    Пользователь должен быть владельцем сервисного центра или администратором.
    """
    address = await service_center_service.get_address(db, address_id=address_id)
    service_center = await service_center_service.get_service_center(db, service_center_id=address.service_center_id)

    # Проверяем права доступа
    if not current_user.is_admin and (not service_center.owner_id or service_center.owner_id != current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для выполнения операции"
        )

    return await service_center_service.delete_address(db, address_id=address_id)


# Эндпоинты для ссылок сервисных центров
@router.get("/{service_center_id}/links/", response_model=List[ServiceCenterLink])
async def read_service_center_links(
        service_center_id: int = Path(..., description="ID сервисного центра"),
        db: AsyncSession = Depends(get_async_db),
        skip: int = Query(0, description="Количество пропускаемых записей"),
        limit: int = Query(settings.DEFAULT_PAGINATION_LIMIT, description="Максимальное количество записей"),
) -> Any:
    """
    Получить ссылки для сервисного центра.
    """
    links, _ = await service_center_service.get_links_by_service_center(
        db, service_center_id=service_center_id, skip=skip, limit=limit
    )
    return links


@router.post("/{service_center_id}/links/", response_model=ServiceCenterLink, status_code=status.HTTP_201_CREATED)
async def create_service_center_link(
        service_center_id: int = Path(..., description="ID сервисного центра"),
        link_in: ServiceCenterLinkCreate = None,
        db: AsyncSession = Depends(get_async_db),
        current_user: User = Depends(get_current_user),
) -> Any:
    """
    Добавить ссылку для сервисного центра.
    Пользователь должен быть владельцем сервисного центра или администратором.
    """
    service_center = await service_center_service.get_service_center(db, service_center_id=service_center_id)

    # Проверяем права доступа
    if not current_user.is_admin and (not service_center.owner_id or service_center.owner_id != current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для выполнения операции"
        )

    # Убедимся, что service_center_id в пути и в теле запроса совпадают
    if link_in.service_center_id != service_center_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID сервисного центра в пути и теле запроса не совпадают"
        )

    return await service_center_service.create_link(db, link_in=link_in)


@router.get("/links/{link_id}", response_model=ServiceCenterLink)
async def read_service_center_link(
        link_id: int = Path(..., description="ID ссылки"),
        db: AsyncSession = Depends(get_async_db),
) -> Any:
    """
    Получить информацию о ссылке по ее ID.
    """
    return await service_center_service.get_link(db, link_id=link_id)


@router.put("/links/{link_id}", response_model=ServiceCenterLink)
async def update_service_center_link(
        link_id: int = Path(..., description="ID ссылки для обновления"),
        link_in: ServiceCenterLinkUpdate = None,
        db: AsyncSession = Depends(get_async_db),
        current_user: User = Depends(get_current_user),
) -> Any:
    """
    Обновить ссылку по ее ID.
    Пользователь должен быть владельцем сервисного центра или администратором.
    """
    link = await service_center_service.get_link(db, link_id=link_id)
    service_center = await service_center_service.get_service_center(db, service_center_id=link.service_center_id)

    # Проверяем права доступа
    if not current_user.is_admin and (not service_center.owner_id or service_center.owner_id != current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для выполнения операции"
        )

    return await service_center_service.update_link(db, link_id=link_id, link_in=link_in)


@router.delete("/links/{link_id}", response_model=ServiceCenterLink)
async def delete_service_center_link(
        link_id: int = Path(..., description="ID ссылки для удаления"),
        db: AsyncSession = Depends(get_async_db),
        current_user: User = Depends(get_current_user),
) -> Any:
    """
    Удалить ссылку по ее ID.
    Пользователь должен быть владельцем сервисного центра или администратором.
    """
    link = await service_center_service.get_link(db, link_id=link_id)
    service_center = await service_center_service.get_service_center(db, service_center_id=link.service_center_id)

    # Проверяем права доступа
    if not current_user.is_admin and (not service_center.owner_id or service_center.owner_id != current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для выполнения операции"
        )

    return await service_center_service.delete_link(db, link_id=link_id)


# Эндпоинты для отзывов и запросов
@router.get("/{service_center_id}/reviews/", response_model=ReviewPagination)
async def read_service_center_reviews(
        service_center_id: int = Path(..., description="ID сервисного центра"),
        db: AsyncSession = Depends(get_async_db),
        skip: int = Query(0, description="Количество пропускаемых записей"),
        limit: int = Query(settings.DEFAULT_PAGINATION_LIMIT, description="Максимальное количество записей"),
) -> Any:
    """
    Получить отзывы для сервисного центра.
    """
    reviews, total = await service_center_service.get_reviews_by_service_center(
        db, service_center_id=service_center_id, skip=skip, limit=limit
    )

    # Вычисляем общее количество страниц
    pages = (total + limit - 1) // limit if limit > 0 else 0

    return {
        "items": reviews,
        "total": total,
        "page": skip // limit + 1 if limit > 0 else 1,
        "size": limit,
        "pages": pages
    }


@router.get("/{service_center_id}/rating/", response_model=Dict[str, Any])
async def get_service_center_rating(
        service_center_id: int = Path(..., description="ID сервисного центра"),
        db: AsyncSession = Depends(get_async_db),
) -> Any:
    """
    Получить рейтинг сервисного центра.
    """
    return await service_center_service.get_service_center_rating(db, service_center_id=service_center_id)


@router.post("/{service_center_id}/reviews/", response_model=Review, status_code=status.HTTP_201_CREATED)
async def create_service_center_review(
        service_center_id: int = Path(..., description="ID сервисного центра"),
        review_in: ReviewCreate = None,
        db: AsyncSession = Depends(get_async_db),
) -> Any:
    """
    Добавить отзыв для сервисного центра.
    """
    # Убедимся, что service_center_id в пути и в теле запроса совпадают
    if review_in.service_center_id != service_center_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID сервисного центра в пути и теле запроса не совпадают"
        )

    return await service_center_service.create_review(db, review_in=review_in)


@router.put("/requests/{request_id}/approve", response_model=AddServiceRequest)
async def approve_service_request(
        request_id: int = Path(..., description="ID запроса для одобрения"),
        owner_id: Optional[int] = Query(None, description="ID пользователя, который станет владельцем (опционально)"),
        db: AsyncSession = Depends(get_async_db),
        current_user: User = Depends(get_current_admin_user),
) -> Any:
    """
    Одобрить запрос на добавление сервисного центра.
    Требуются права администратора.
    """
    return await service_center_service.approve_request(db, request_id=request_id, owner_id=owner_id)


@router.put("/requests/{request_id}/reject", response_model=AddServiceRequest)
async def reject_service_request(
        request_id: int = Path(..., description="ID запроса для отклонения"),
        db: AsyncSession = Depends(get_async_db),
        current_user: User = Depends(get_current_admin_user),
) -> Any:
    """
    Отклонить запрос на добавление сервисного центра.
    Требуются права администратора.
    """
    return await service_center_service.reject_request(db, request_id=request_id)