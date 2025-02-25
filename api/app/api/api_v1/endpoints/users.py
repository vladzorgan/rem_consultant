from typing import Any, List
from fastapi import APIRouter, Depends, Query, Path, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_async_db, get_current_admin_user
from app.services.user_service import user_service
from app.schemas.user import User, UserCreate, UserUpdate, UserPagination, UserRole
from app.core.config import settings

router = APIRouter()


@router.get("/", response_model=UserPagination)
async def read_users(
        db: AsyncSession = Depends(get_async_db),
        skip: int = Query(0, description="Количество пропускаемых записей"),
        limit: int = Query(settings.DEFAULT_PAGINATION_LIMIT, description="Максимальное количество записей"),
        current_user: User = Depends(get_current_admin_user),
) -> Any:
    """
    Получить список всех пользователей с пагинацией.
    Требуются права администратора.
    """
    users, total = await user_service.get_users(db, skip=skip, limit=limit)

    # Вычисляем общее количество страниц
    pages = (total + limit - 1) // limit if limit > 0 else 0

    return {
        "items": users,
        "total": total,
        "page": skip // limit + 1 if limit > 0 else 1,
        "size": limit,
        "pages": pages
    }


@router.get("/search/", response_model=UserPagination)
async def search_users(
        keyword: str = Query(..., description="Ключевое слово для поиска"),
        db: AsyncSession = Depends(get_async_db),
        skip: int = Query(0, description="Количество пропускаемых записей"),
        limit: int = Query(settings.DEFAULT_PAGINATION_LIMIT, description="Максимальное количество записей"),
        current_user: User = Depends(get_current_admin_user),
) -> Any:
    """
    Поиск пользователей по ключевому слову (email или имя).
    Требуются права администратора.
    """
    users, total = await user_service.search_users(db, keyword=keyword, skip=skip, limit=limit)

    # Вычисляем общее количество страниц
    pages = (total + limit - 1) // limit if limit > 0 else 0

    return {
        "items": users,
        "total": total,
        "page": skip // limit + 1 if limit > 0 else 1,
        "size": limit,
        "pages": pages
    }


@router.get("/service-owners/", response_model=UserPagination)
async def read_service_owners(
        db: AsyncSession = Depends(get_async_db),
        skip: int = Query(0, description="Количество пропускаемых записей"),
        limit: int = Query(settings.DEFAULT_PAGINATION_LIMIT, description="Максимальное количество записей"),
        current_user: User = Depends(get_current_admin_user),
) -> Any:
    """
    Получить список всех владельцев сервисных центров.
    Требуются права администратора.
    """
    users, total = await user_service.get_service_owners(db, skip=skip, limit=limit)

    # Вычисляем общее количество страниц
    pages = (total + limit - 1) // limit if limit > 0 else 0

    return {
        "items": users,
        "total": total,
        "page": skip // limit + 1 if limit > 0 else 1,
        "size": limit,
        "pages": pages
    }


@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(
        user_in: UserCreate,
        db: AsyncSession = Depends(get_async_db),
        current_user: User = Depends(get_current_admin_user),
) -> Any:
    """
    Создать нового пользователя.
    Требуются права администратора.
    """
    return await user_service.register_user(db, user_data=user_in)


@router.get("/{user_id}", response_model=User)
async def read_user(
        user_id: int = Path(..., description="ID пользователя для получения"),
        db: AsyncSession = Depends(get_async_db),
        current_user: User = Depends(get_current_admin_user),
) -> Any:
    """
    Получить информацию о пользователе по его ID.
    Требуются права администратора.
    """
    return await user_service.get_user(db, user_id=user_id)


@router.put("/{user_id}", response_model=User)
async def update_user(
        user_id: int = Path(..., description="ID пользователя для обновления"),
        user_in: UserUpdate = None,
        db: AsyncSession = Depends(get_async_db),
        current_user: User = Depends(get_current_admin_user),
) -> Any:
    """
    Обновить информацию о пользователе по его ID.
    Требуются права администратора.
    """
    return await user_service.update_user(db, user_id=user_id, user_in=user_in)


@router.put("/{user_id}/deactivate", response_model=User)
async def deactivate_user(
        user_id: int = Path(..., description="ID пользователя для деактивации"),
        db: AsyncSession = Depends(get_async_db),
        current_user: User = Depends(get_current_admin_user),
) -> Any:
    """
    Деактивировать пользователя по его ID.
    Требуются права администратора.
    """
    return await user_service.deactivate_user(db, user_id=user_id)


@router.delete("/{user_id}", response_model=User)
async def delete_user(
        user_id: int = Path(..., description="ID пользователя для удаления"),
        db: AsyncSession = Depends(get_async_db),
        current_user: User = Depends(get_current_admin_user),
) -> Any:
    """
    Удалить пользователя по его ID.
    Требуются права администратора.
    """
    return await user_service.delete_user(db, user_id=user_id)


@router.put("/{user_id}/promote-to-service-owner", response_model=User)
async def promote_to_service_owner(
        user_id: int = Path(..., description="ID пользователя для повышения"),
        db: AsyncSession = Depends(get_async_db),
        current_user: User = Depends(get_current_admin_user),
) -> Any:
    """
    Повысить пользователя до владельца сервисного центра.
    Требуются права администратора.
    """
    user = await user_service.get_user(db, user_id=user_id)
    user_update = UserUpdate(role=UserRole.SERVICE_OWNER)
    return await user_service.update_user(db, user_id=user_id, user_in=user_update)


@router.put("/{user_id}/promote-to-admin", response_model=User)
async def promote_to_admin(
        user_id: int = Path(..., description="ID пользователя для повышения"),
        db: AsyncSession = Depends(get_async_db),
        current_user: User = Depends(get_current_admin_user),
) -> Any:
    """
    Повысить пользователя до администратора.
    Требуются права администратора.
    """
    user = await user_service.get_user(db, user_id=user_id)
    user_update = UserUpdate(role=UserRole.ADMIN)
    return await user_service.update_user(db, user_id=user_id, user_in=user_update)


@router.get("/by-email/{email}", response_model=User)
async def read_user_by_email(
        email: str = Path(..., description="Email пользователя для получения"),
        db: AsyncSession = Depends(get_async_db),
        current_user: User = Depends(get_current_admin_user),
) -> Any:
    """
    Получить информацию о пользователе по его email.
    Требуются права администратора.
    """
    user = await user_service.get_user_by_email(db, email=email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Пользователь с email {email} не найден"
        )
    return user