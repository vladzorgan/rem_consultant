from typing import List, Optional, Dict, Any
from sqlalchemy import select, or_, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload

from app.models.service import (
    ServiceCenter, ServiceCenterAddress, ServiceCenterLink, Review, AddServiceRequest
)
from app.schemas.service_center import (
    ServiceCenterCreate, ServiceCenterUpdate, ServiceCenterAddressCreate, ServiceCenterAddressUpdate,
    ServiceCenterLinkCreate, ServiceCenterLinkUpdate, ReviewCreate, ReviewUpdate,
    AddServiceRequestCreate, AddServiceRequestUpdate
)
from app.repositories.base import BaseRepository


class ServiceCenterRepository(BaseRepository[ServiceCenter, ServiceCenterCreate, ServiceCenterUpdate]):
    def __init__(self):
        super().__init__(ServiceCenter)

    async def get_with_relations(self, db: AsyncSession, id: int) -> Optional[ServiceCenter]:
        """
        Получить сервисный центр с загрузкой связанных данных
        """
        query = select(ServiceCenter).where(ServiceCenter.id == id).options(
            selectinload(ServiceCenter.addresses),
            selectinload(ServiceCenter.links),
            selectinload(ServiceCenter.reviews),
            joinedload(ServiceCenter.city),
            joinedload(ServiceCenter.owner)
        )
        result = await db.execute(query)
        return result.scalars().first()

    async def get_by_name(self, db: AsyncSession, name: str, city_id: Optional[int] = None) -> Optional[ServiceCenter]:
        """
        Поиск сервисного центра по имени и опционально по городу
        """
        conditions = [func.lower(ServiceCenter.name) == func.lower(name)]

        if city_id is not None:
            conditions.append(ServiceCenter.city_id == city_id)

        query = select(ServiceCenter).where(and_(*conditions))
        result = await db.execute(query)
        return result.scalars().first()

    async def search(
            self, db: AsyncSession, *, keyword: str, city_id: Optional[int] = None,
            skip: int = 0, limit: int = 100
    ) -> List[ServiceCenter]:
        """
        Поиск сервисных центров по ключевому слову и опционально по городу
        """
        conditions = [func.lower(ServiceCenter.name).contains(func.lower(keyword))]

        if city_id is not None:
            conditions.append(ServiceCenter.city_id == city_id)

        query = (
            select(ServiceCenter)
            .where(and_(*conditions))
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        return result.scalars().all()

    async def get_by_city(
            self, db: AsyncSession, *, city_id: int, skip: int = 0, limit: int = 100
    ) -> List[ServiceCenter]:
        """
        Получить сервисные центры по ID города
        """
        query = (
            select(ServiceCenter)
            .where(ServiceCenter.city_id == city_id)
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        return result.scalars().all()

    async def get_by_owner(
            self, db: AsyncSession, *, owner_id: int, skip: int = 0, limit: int = 100
    ) -> List[ServiceCenter]:
        """
        Получить сервисные центры по ID владельца
        """
        query = (
            select(ServiceCenter)
            .where(ServiceCenter.owner_id == owner_id)
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        return result.scalars().all()

    async def get_with_best_rating(
            self, db: AsyncSession, *, limit: int = 10
    ) -> List[ServiceCenter]:
        """
        Получить сервисные центры с лучшим рейтингом
        """
        # Подзапрос для получения среднего рейтинга
        from sqlalchemy import desc

        query = (
            select(ServiceCenter)
            .join(ServiceCenter.reviews)
            .group_by(ServiceCenter.id)
            .order_by(desc(func.avg(Review.rating)))
            .limit(limit)
        )
        result = await db.execute(query)
        return result.scalars().all()


class ServiceCenterAddressRepository(
    BaseRepository[ServiceCenterAddress, ServiceCenterAddressCreate, ServiceCenterAddressUpdate]):
    def __init__(self):
        super().__init__(ServiceCenterAddress)

    async def get_by_service_center(
            self, db: AsyncSession, *, service_center_id: int, skip: int = 0, limit: int = 100
    ) -> List[ServiceCenterAddress]:
        """
        Получить адреса для заданного сервисного центра
        """
        query = (
            select(ServiceCenterAddress)
            .where(ServiceCenterAddress.service_center_id == service_center_id)
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        return result.scalars().all()


class ServiceCenterLinkRepository(BaseRepository[ServiceCenterLink, ServiceCenterLinkCreate, ServiceCenterLinkUpdate]):
    def __init__(self):
        super().__init__(ServiceCenterLink)

    async def get_by_service_center(
            self, db: AsyncSession, *, service_center_id: int, skip: int = 0, limit: int = 100
    ) -> List[ServiceCenterLink]:
        """
        Получить ссылки для заданного сервисного центра
        """
        query = (
            select(ServiceCenterLink)
            .where(ServiceCenterLink.service_center_id == service_center_id)
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        return result.scalars().all()


class ReviewRepository(BaseRepository[Review, ReviewCreate, ReviewUpdate]):
    def __init__(self):
        super().__init__(Review)

    async def get_by_service_center(
            self, db: AsyncSession, *, service_center_id: int, skip: int = 0, limit: int = 100
    ) -> List[Review]:
        """
        Получить отзывы для заданного сервисного центра
        """
        query = (
            select(Review)
            .where(Review.service_center_id == service_center_id)
            .order_by(Review.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        return result.scalars().all()

    async def get_service_center_rating(self, db: AsyncSession, *, service_center_id: int) -> Dict[str, Any]:
        """
        Получить рейтинг сервисного центра
        """
        query = select(
            func.avg(Review.rating).label("avg_rating"),
            func.count(Review.id).label("count")
        ).where(Review.service_center_id == service_center_id)

        result = await db.execute(query)
        stats = result.fetchone()

        if not stats or not stats.avg_rating:
            return {
                "average_rating": 0,
                "count": 0
            }

        return {
            "average_rating": float(stats.avg_rating),
            "count": stats.count
        }


class AddServiceRequestRepository(BaseRepository[AddServiceRequest, AddServiceRequestCreate, AddServiceRequestUpdate]):
    def __init__(self):
        super().__init__(AddServiceRequest)

    async def get_by_service_center(
            self, db: AsyncSession, *, service_center_id: int, skip: int = 0, limit: int = 100
    ) -> List[AddServiceRequest]:
        """
        Получить запросы для заданного сервисного центра
        """
        query = (
            select(AddServiceRequest)
            .where(AddServiceRequest.service_center_id == service_center_id)
            .order_by(AddServiceRequest.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        return result.scalars().all()

    async def get_by_telegram_id(
            self, db: AsyncSession, *, telegram_id: int, skip: int = 0, limit: int = 100
    ) -> List[AddServiceRequest]:
        """
        Получить запросы для заданного Telegram ID
        """
        query = (
            select(AddServiceRequest)
            .where(AddServiceRequest.telegram_id == telegram_id)
            .order_by(AddServiceRequest.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        return result.scalars().all()

    async def get_pending_requests(
            self, db: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> List[AddServiceRequest]:
        """
        Получить ожидающие запросы
        """
        from app.models.common import RequestStatus

        query = (
            select(AddServiceRequest)
            .where(AddServiceRequest.status == RequestStatus.PENDING)
            .order_by(AddServiceRequest.created_at)
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        return result.scalars().all()