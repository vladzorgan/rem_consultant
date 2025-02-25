from typing import List, Optional, Tuple, Dict, Any
from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.service_center import (
    ServiceCenterRepository, ServiceCenterAddressRepository,
    ServiceCenterLinkRepository, ReviewRepository, AddServiceRequestRepository
)
from app.schemas.service_center import (
    ServiceCenterCreate, ServiceCenterUpdate, ServiceCenter, ServiceCenterDetail,
    ServiceCenterAddressCreate, ServiceCenterAddressUpdate, ServiceCenterAddress,
    ServiceCenterLinkCreate, ServiceCenterLinkUpdate, ServiceCenterLink,
    ReviewCreate, ReviewUpdate, Review,
    AddServiceRequestCreate, AddServiceRequestUpdate, AddServiceRequest
)

from app.models.common import RequestStatus


class ServiceCenterService:
    def __init__(self):
        self.service_center_repository = ServiceCenterRepository()
        self.address_repository = ServiceCenterAddressRepository()
        self.link_repository = ServiceCenterLinkRepository()
        self.review_repository = ReviewRepository()
        self.request_repository = AddServiceRequestRepository()

    # -- Операции с сервисными центрами --

    async def get_service_center(self, db: AsyncSession, service_center_id: int) -> ServiceCenter:
        """Получить сервисный центр по ID"""
        service_center = await self.service_center_repository.get(db, service_center_id)
        if not service_center:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Сервисный центр с ID {service_center_id} не найден"
            )
        return service_center

    async def get_service_center_with_relations(self, db: AsyncSession, service_center_id: int) -> ServiceCenterDetail:
        """Получить сервисный центр с загрузкой связанных данных"""
        service_center = await self.service_center_repository.get_with_relations(db, service_center_id)
        if not service_center:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Сервисный центр с ID {service_center_id} не найден"
            )
        return service_center

    async def get_service_centers(
            self, db: AsyncSession, skip: int = 0, limit: int = 100
    ) -> Tuple[List[ServiceCenter], int]:
        """Получить список сервисных центров с пагинацией"""
        service_centers = await self.service_center_repository.get_multi(db, skip=skip, limit=limit)
        total = await self.service_center_repository.get_count(db)
        return service_centers, total

    async def search_service_centers(
            self, db: AsyncSession, keyword: str, city_id: Optional[int] = None,
            skip: int = 0, limit: int = 100
    ) -> Tuple[List[ServiceCenter], int]:
        """Поиск сервисных центров по ключевому слову и опционально по городу"""
        service_centers = await self.service_center_repository.search(
            db, keyword=keyword, city_id=city_id, skip=skip, limit=limit
        )

        # Для получения общего числа совпадений используем отдельный запрос
        from sqlalchemy import or_, and_
        conditions = [func.lower(self.service_center_repository.model.name).contains(func.lower(keyword))]

        if city_id is not None:
            conditions.append(self.service_center_repository.model.city_id == city_id)

        query = self.service_center_repository.model.__table__.select().where(and_(*conditions))
        total = await self.service_center_repository.get_count(db, query)

        return service_centers, total

    async def get_service_centers_by_city(
            self, db: AsyncSession, city_id: int, skip: int = 0, limit: int = 100
    ) -> Tuple[List[ServiceCenter], int]:
        """Получить сервисные центры по ID города"""
        service_centers = await self.service_center_repository.get_by_city(
            db, city_id=city_id, skip=skip, limit=limit
        )

        # Получаем общее число сервисных центров для этого города
        from sqlalchemy import select, func
        query = select(func.count()).where(
            self.service_center_repository.model.city_id == city_id
        ).select_from(self.service_center_repository.model)

        result = await db.execute(query)
        total = result.scalar_one()

        return service_centers, total

    async def get_service_centers_by_owner(
            self, db: AsyncSession, owner_id: int, skip: int = 0, limit: int = 100
    ) -> Tuple[List[ServiceCenter], int]:
        """Получить сервисные центры по ID владельца"""
        service_centers = await self.service_center_repository.get_by_owner(
            db, owner_id=owner_id, skip=skip, limit=limit
        )

        # Получаем общее число сервисных центров для этого владельца
        from sqlalchemy import select, func
        query = select(func.count()).where(
            self.service_center_repository.model.owner_id == owner_id
        ).select_from(self.service_center_repository.model)

        result = await db.execute(query)
        total = result.scalar_one()

        return service_centers, total

    async def get_top_rated_service_centers(
            self, db: AsyncSession, limit: int = 10
    ) -> List[ServiceCenter]:
        """Получить сервисные центры с лучшим рейтингом"""
        return await self.service_center_repository.get_with_best_rating(db, limit=limit)

    async def create_service_center(self, db: AsyncSession, service_center_in: ServiceCenterCreate) -> ServiceCenter:
        """Создать новый сервисный центр"""
        # Проверяем, существует ли сервисный центр с таким названием в этом городе
        if service_center_in.city_id:
            existing_service_center = await self.service_center_repository.get_by_name(
                db, name=service_center_in.name, city_id=service_center_in.city_id
            )

            if existing_service_center:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Сервисный центр с названием '{service_center_in.name}' уже существует в этом городе"
                )

        # Проверяем существование города, если он указан
        if service_center_in.city_id:
            from app.services.location_service import location_service
            await location_service.get_city(db, service_center_in.city_id)

        # Проверяем существование владельца, если он указан
        if service_center_in.owner_id:
            from app.services.user_service import user_service
            await user_service.get_user(db, service_center_in.owner_id)

        return await self.service_center_repository.create(db, obj_in=service_center_in)

    async def update_service_center(
            self, db: AsyncSession, service_center_id: int, service_center_in: ServiceCenterUpdate
    ) -> ServiceCenter:
        """Обновить существующий сервисный центр"""
        service_center = await self.get_service_center(db, service_center_id)

        # Если обновляется название или город, проверяем уникальность
        if (service_center_in.name and service_center_in.name != service_center.name) or \
                (service_center_in.city_id and service_center_in.city_id != service_center.city_id):

            name = service_center_in.name or service_center.name
            city_id = service_center_in.city_id or service_center.city_id

            if city_id:
                existing_service_center = await self.service_center_repository.get_by_name(
                    db, name=name, city_id=city_id
                )

                if existing_service_center and existing_service_center.id != service_center_id:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Сервисный центр с названием '{name}' уже существует в этом городе"
                    )

        # Проверяем существование города, если он меняется
        if service_center_in.city_id and service_center_in.city_id != service_center.city_id:
            from app.services.location_service import location_service
            await location_service.get_city(db, service_center_in.city_id)

        # Проверяем существование владельца, если он меняется
        if service_center_in.owner_id and service_center_in.owner_id != service_center.owner_id:
            from app.services.user_service import user_service
            await user_service.get_user(db, service_center_in.owner_id)

        return await self.service_center_repository.update(db, db_obj=service_center, obj_in=service_center_in)

    async def delete_service_center(self, db: AsyncSession, service_center_id: int) -> ServiceCenter:
        """Удалить сервисный центр по ID"""
        service_center = await self.get_service_center(db, service_center_id)
        return await self.service_center_repository.remove(db, id=service_center_id)

    # -- Операции с адресами сервисных центров --
    async def get_address(self, db: AsyncSession, address_id: int) -> ServiceCenterAddress:
        """Получить адрес по ID"""
        address = await self.address_repository.get(db, address_id)
        if not address:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Адрес с ID {address_id} не найден"
            )
        return address

    async def get_addresses_by_service_center(
            self, db: AsyncSession, service_center_id: int, skip: int = 0, limit: int = 100
    ) -> Tuple[List[ServiceCenterAddress], int]:
        """Получить адреса сервисного центра"""
        addresses = await self.address_repository.get_by_service_center(
            db, service_center_id=service_center_id, skip=skip, limit=limit
        )

        # Получаем общее число адресов для этого сервисного центра
        from sqlalchemy import select, func
        query = select(func.count()).where(
            self.address_repository.model.service_center_id == service_center_id
        ).select_from(self.address_repository.model)

        result = await db.execute(query)
        total = result.scalar_one()

        return addresses, total

    async def create_address(self, db: AsyncSession, address_in: ServiceCenterAddressCreate) -> ServiceCenterAddress:
        """Создать новый адрес для сервисного центра"""
        # Проверяем существование сервисного центра
        await self.get_service_center(db, address_in.service_center_id)

        return await self.address_repository.create(db, obj_in=address_in)

    async def update_address(
            self, db: AsyncSession, address_id: int, address_in: ServiceCenterAddressUpdate
    ) -> ServiceCenterAddress:
        """Обновить адрес сервисного центра"""
        address = await self.get_address(db, address_id)

        # Если меняется сервисный центр, проверяем его существование
        if address_in.service_center_id and address_in.service_center_id != address.service_center_id:
            await self.get_service_center(db, address_in.service_center_id)

        return await self.address_repository.update(db, db_obj=address, obj_in=address_in)

    async def delete_address(self, db: AsyncSession, address_id: int) -> ServiceCenterAddress:
        """Удалить адрес сервисного центра"""
        address = await self.get_address(db, address_id)
        return await self.address_repository.remove(db, id=address_id)

    # -- Операции со ссылками сервисных центров --

    async def get_link(self, db: AsyncSession, link_id: int) -> ServiceCenterLink:
        """Получить ссылку по ID"""
        link = await self.link_repository.get(db, link_id)
        if not link:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Ссылка с ID {link_id} не найдена"
            )
        return link

    async def get_links_by_service_center(
            self, db: AsyncSession, service_center_id: int, skip: int = 0, limit: int = 100
    ) -> Tuple[List[ServiceCenterLink], int]:
        """Получить ссылки сервисного центра"""
        links = await self.link_repository.get_by_service_center(
            db, service_center_id=service_center_id, skip=skip, limit=limit
        )

        # Получаем общее число ссылок для этого сервисного центра
        from sqlalchemy import select, func
        query = select(func.count()).where(
            self.link_repository.model.service_center_id == service_center_id
        ).select_from(self.link_repository.model)

        result = await db.execute(query)
        total = result.scalar_one()

        return links, total

    async def create_link(self, db: AsyncSession, link_in: ServiceCenterLinkCreate) -> ServiceCenterLink:
        """Создать новую ссылку для сервисного центра"""
        # Проверяем существование сервисного центра
        await self.get_service_center(db, link_in.service_center_id)

        return await self.link_repository.create(db, obj_in=link_in)

    async def update_link(
            self, db: AsyncSession, link_id: int, link_in: ServiceCenterLinkUpdate
    ) -> ServiceCenterLink:
        """Обновить ссылку сервисного центра"""
        link = await self.get_link(db, link_id)

        # Если меняется сервисный центр, проверяем его существование
        if link_in.service_center_id and link_in.service_center_id != link.service_center_id:
            await self.get_service_center(db, link_in.service_center_id)

        return await self.link_repository.update(db, db_obj=link, obj_in=link_in)

    async def delete_link(self, db: AsyncSession, link_id: int) -> ServiceCenterLink:
        """Удалить ссылку сервисного центра"""
        link = await self.get_link(db, link_id)
        return await self.link_repository.remove(db, id=link_id)

    # -- Операции с отзывами --

    async def get_review(self, db: AsyncSession, review_id: int) -> Review:
        """Получить отзыв по ID"""
        review = await self.review_repository.get(db, review_id)
        if not review:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Отзыв с ID {review_id} не найден"
            )
        return review

    async def get_reviews_by_service_center(
            self, db: AsyncSession, service_center_id: int, skip: int = 0, limit: int = 100
    ) -> Tuple[List[Review], int]:
        """Получить отзывы сервисного центра"""
        reviews = await self.review_repository.get_by_service_center(
            db, service_center_id=service_center_id, skip=skip, limit=limit
        )

        # Получаем общее число отзывов для этого сервисного центра
        from sqlalchemy import select, func
        query = select(func.count()).where(
            self.review_repository.model.service_center_id == service_center_id
        ).select_from(self.review_repository.model)

        result = await db.execute(query)
        total = result.scalar_one()

        return reviews, total

    async def get_service_center_rating(self, db: AsyncSession, service_center_id: int) -> Dict[str, Any]:
        """Получить рейтинг сервисного центра"""
        # Проверяем существование сервисного центра
        await self.get_service_center(db, service_center_id)

        return await self.review_repository.get_service_center_rating(db, service_center_id=service_center_id)

    async def create_review(self, db: AsyncSession, review_in: ReviewCreate) -> Review:
        """Создать новый отзыв для сервисного центра"""
        # Проверяем существование сервисного центра
        await self.get_service_center(db, review_in.service_center_id)

        return await self.review_repository.create(db, obj_in=review_in)

    async def update_review(
            self, db: AsyncSession, review_id: int, review_in: ReviewUpdate
    ) -> Review:
        """Обновить отзыв"""
        review = await self.get_review(db, review_id)

        # Если меняется сервисный центр, проверяем его существование
        if review_in.service_center_id and review_in.service_center_id != review.service_center_id:
            await self.get_service_center(db, review_in.service_center_id)

        return await self.review_repository.update(db, db_obj=review, obj_in=review_in)

    async def delete_review(self, db: AsyncSession, review_id: int) -> Review:
        """Удалить отзыв"""
        review = await self.get_review(db, review_id)
        return await self.review_repository.remove(db, id=review_id)

    # -- Операции с запросами на добавление сервисного центра --

    async def get_request(self, db: AsyncSession, request_id: int) -> AddServiceRequest:
        """Получить запрос по ID"""
        request = await self.request_repository.get(db, request_id)
        if not request:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Запрос с ID {request_id} не найден"
            )
        return request

    async def get_requests_by_service_center(
            self, db: AsyncSession, service_center_id: int, skip: int = 0, limit: int = 100
    ) -> Tuple[List[AddServiceRequest], int]:
        """Получить запросы для сервисного центра"""
        requests = await self.request_repository.get_by_service_center(
            db, service_center_id=service_center_id, skip=skip, limit=limit
        )

        # Получаем общее число запросов для этого сервисного центра
        from sqlalchemy import select, func
        query = select(func.count()).where(
            self.request_repository.model.service_center_id == service_center_id
        ).select_from(self.request_repository.model)

        result = await db.execute(query)
        total = result.scalar_one()

        return requests, total

    async def get_requests_by_telegram_id(
            self, db: AsyncSession, telegram_id: int, skip: int = 0, limit: int = 100
    ) -> Tuple[List[AddServiceRequest], int]:
        """Получить запросы по Telegram ID"""
        requests = await self.request_repository.get_by_telegram_id(
            db, telegram_id=telegram_id, skip=skip, limit=limit
        )

        # Получаем общее число запросов для этого Telegram ID
        from sqlalchemy import select, func
        query = select(func.count()).where(
            self.request_repository.model.telegram_id == telegram_id
        ).select_from(self.request_repository.model)

        result = await db.execute(query)
        total = result.scalar_one()

        return requests, total

    async def get_pending_requests(
            self, db: AsyncSession, skip: int = 0, limit: int = 100
    ) -> Tuple[List[AddServiceRequest], int]:
        """Получить ожидающие запросы"""
        requests = await self.request_repository.get_pending_requests(db, skip=skip, limit=limit)

        # Получаем общее число ожидающих запросов
        from sqlalchemy import select, func
        query = select(func.count()).where(
            self.request_repository.model.status == RequestStatus.PENDING
        ).select_from(self.request_repository.model)

        result = await db.execute(query)
        total = result.scalar_one()

        return requests, total

    async def create_request(self, db: AsyncSession, request_in: AddServiceRequestCreate) -> AddServiceRequest:
        """Создать новый запрос на добавление сервисного центра"""
        # Проверяем существование сервисного центра
        await self.get_service_center(db, request_in.service_center_id)

        return await self.request_repository.create(db, obj_in=request_in)

    async def update_request(
            self, db: AsyncSession, request_id: int, request_in: AddServiceRequestUpdate
    ) -> AddServiceRequest:
        """Обновить запрос"""
        request = await self.get_request(db, request_id)

        # Если меняется сервисный центр, проверяем его существование
        if request_in.service_center_id and request_in.service_center_id != request.service_center_id:
            await self.get_service_center(db, request_in.service_center_id)

        return await self.request_repository.update(db, db_obj=request, obj_in=request_in)

    async def approve_request(self, db: AsyncSession, request_id: int,
                              owner_id: Optional[int] = None) -> AddServiceRequest:
        """Одобрить запрос на добавление сервисного центра"""
        request = await self.get_request(db, request_id)

        # Если запрос уже обработан, выдаем ошибку
        if request.status != RequestStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Запрос уже обработан (статус: {request.status.value})"
            )

        # Обновляем статус запроса
        update_data = {"status": RequestStatus.APPROVED}

        # Если указан owner_id, обновляем владельца сервисного центра
        if owner_id:
            # Проверяем существование пользователя
            from app.services.user_service import user_service
            await user_service.get_user(db, owner_id)

            # Обновляем сервисный центр
            await self.service_center_repository.update(
                db,
                db_obj=request.service_center,
                obj_in={"owner_id": owner_id}
            )

        return await self.request_repository.update(db, db_obj=request, obj_in=update_data)

    async def reject_request(self, db: AsyncSession, request_id: int) -> AddServiceRequest:
        """Отклонить запрос на добавление сервисного центра"""
        request = await self.get_request(db, request_id)

        # Если запрос уже обработан, выдаем ошибку
        if request.status != RequestStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Запрос уже обработан (статус: {request.status.value})"
            )

        # Обновляем статус запроса
        update_data = {"status": RequestStatus.REJECTED}
        return await self.request_repository.update(db, db_obj=request, obj_in=update_data)

    async def delete_request(self, db: AsyncSession, request_id: int) -> AddServiceRequest:
        """Удалить запрос"""
        request = await self.get_request(db, request_id)
        return await self.request_repository.remove(db, id=request_id)


# Экспортируем экземпляр сервиса для использования в API
service_center_service = ServiceCenterService()