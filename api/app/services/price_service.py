from typing import List, Optional, Tuple, Dict, Any
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.repair import (
    ModelRepairRepository, RepairPriceRepository, PriceRepository
)
from app.schemas.repair import (
    ModelRepairCreate, ModelRepairUpdate, ModelRepair,
    RepairPriceCreate, RepairPriceUpdate, RepairPrice,
    PriceCreate, PriceUpdate, Price,
    PriceAnalysis
)


class PriceService:
    def __init__(self):
        self.model_repair_repository = ModelRepairRepository()
        self.repair_price_repository = RepairPriceRepository()
        self.price_repository = PriceRepository()

    # -- Операции с ModelRepair (связь модель-тип ремонта) --

    async def get_model_repair(self, db: AsyncSession, model_repair_id: int) -> ModelRepair:
        """Получить связь модель-тип ремонта по ID"""
        model_repair = await self.model_repair_repository.get(db, model_repair_id)
        if not model_repair:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Связь модель-тип ремонта с ID {model_repair_id} не найдена"
            )
        return model_repair

    async def get_model_repair_with_relations(self, db: AsyncSession, model_repair_id: int) -> ModelRepair:
        """Получить связь модель-тип ремонта с загрузкой связанных данных"""
        model_repair = await self.model_repair_repository.get_with_relations(db, model_repair_id)
        if not model_repair:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Связь модель-тип ремонта с ID {model_repair_id} не найдена"
            )
        return model_repair

    async def get_model_repairs_by_model(
            self, db: AsyncSession, model_id: int, skip: int = 0, limit: int = 100
    ) -> Tuple[List[ModelRepair], int]:
        """Получить типы ремонта для модели устройства"""
        model_repairs = await self.model_repair_repository.get_by_model(
            db, model_id=model_id, skip=skip, limit=limit
        )

        # Получаем общее число типов ремонта для этой модели
        from sqlalchemy import select, func
        query = select(func.count()).where(
            self.model_repair_repository.model.model_id == model_id
        ).select_from(self.model_repair_repository.model)

        result = await db.execute(query)
        total = result.scalar_one()

        return model_repairs, total

    async def get_model_repairs_by_repair_type(
            self, db: AsyncSession, repair_type_id: int, skip: int = 0, limit: int = 100
    ) -> Tuple[List[ModelRepair], int]:
        """Получить модели для типа ремонта"""
        model_repairs = await self.model_repair_repository.get_by_repair_type(
            db, repair_type_id=repair_type_id, skip=skip, limit=limit
        )

        # Получаем общее число моделей для этого типа ремонта
        from sqlalchemy import select, func
        query = select(func.count()).where(
            self.model_repair_repository.model.repair_type_id == repair_type_id
        ).select_from(self.model_repair_repository.model)

        result = await db.execute(query)
        total = result.scalar_one()

        return model_repairs, total

    async def create_model_repair(self, db: AsyncSession, model_repair_in: ModelRepairCreate) -> ModelRepair:
        """Добавить тип ремонта к модели устройства"""
        # Проверяем, существует ли уже такая связь
        existing_model_repair = await self.model_repair_repository.get_by_model_and_repair_type(
            db, model_id=model_repair_in.model_id, repair_type_id=model_repair_in.repair_type_id
        )

        if existing_model_repair:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Этот тип ремонта уже добавлен к данной модели устройства"
            )

        # Проверяем существование связанных сущностей
        from app.services.repair_service import repair_service
        from app.services.device_service import device_service

        # Проверка существования модели устройства
        await device_service.get_model(db, model_repair_in.model_id)

        # Проверка существования типа ремонта
        await repair_service.get_repair_type(db, model_repair_in.repair_type_id)

        return await self.model_repair_repository.create(db, obj_in=model_repair_in)

    async def update_model_repair(
            self, db: AsyncSession, model_repair_id: int, model_repair_in: ModelRepairUpdate
    ) -> ModelRepair:
        """Обновить связь модель-тип ремонта"""
        model_repair = await self.get_model_repair(db, model_repair_id)

        # Если меняется модель или тип ремонта, проверяем уникальность связи
        if (model_repair_in.model_id and model_repair_in.model_id != model_repair.model_id) or \
                (model_repair_in.repair_type_id and model_repair_in.repair_type_id != model_repair.repair_type_id):

            model_id = model_repair_in.model_id or model_repair.model_id
            repair_type_id = model_repair_in.repair_type_id or model_repair.repair_type_id

            existing_model_repair = await self.model_repair_repository.get_by_model_and_repair_type(
                db, model_id=model_id, repair_type_id=repair_type_id
            )

            if existing_model_repair and existing_model_repair.id != model_repair_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Этот тип ремонта уже добавлен к данной модели устройства"
                )

            # Проверяем существование связанных сущностей
            from app.services.repair_service import repair_service
            from app.services.device_service import device_service

            if model_repair_in.model_id:
                await device_service.get_model(db, model_repair_in.model_id)

            if model_repair_in.repair_type_id:
                await repair_service.get_repair_type(db, model_repair_in.repair_type_id)

        return await self.model_repair_repository.update(db, db_obj=model_repair, obj_in=model_repair_in)

    async def delete_model_repair(self, db: AsyncSession, model_repair_id: int) -> ModelRepair:
        """Удалить связь модель-тип ремонта"""
        model_repair = await self.get_model_repair(db, model_repair_id)
        return await self.model_repair_repository.remove(db, id=model_repair_id)

    # -- Операции с RepairPrice (стандартная цена на ремонт) --

    async def get_repair_price(self, db: AsyncSession, repair_price_id: int) -> RepairPrice:
        """Получить цену на ремонт по ID"""
        repair_price = await self.repair_price_repository.get(db, repair_price_id)
        if not repair_price:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Цена на ремонт с ID {repair_price_id} не найдена"
            )
        return repair_price

    async def get_repair_price_with_relations(self, db: AsyncSession, repair_price_id: int) -> RepairPrice:
        """Получить цену на ремонт с загрузкой связанных данных"""
        repair_price = await self.repair_price_repository.get_with_relations(db, repair_price_id)
        if not repair_price:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Цена на ремонт с ID {repair_price_id} не найдена"
            )
        return repair_price

    async def get_repair_prices_by_model(
            self, db: AsyncSession, device_model_id: int, skip: int = 0, limit: int = 100
    ) -> Tuple[List[RepairPrice], int]:
        """Получить цены на ремонт для модели устройства"""
        repair_prices = await self.repair_price_repository.get_by_model(
            db, device_model_id=device_model_id, skip=skip, limit=limit
        )

        # Получаем общее число цен для этой модели
        from sqlalchemy import select, func
        query = select(func.count()).where(
            self.repair_price_repository.model.device_model_id == device_model_id
        ).select_from(self.repair_price_repository.model)

        result = await db.execute(query)
        total = result.scalar_one()

        return repair_prices, total

    async def get_repair_prices_by_repair(
            self, db: AsyncSession, repair_id: int, skip: int = 0, limit: int = 100
    ) -> Tuple[List[RepairPrice], int]:
        """Получить цены на ремонт для типа ремонта"""
        repair_prices = await self.repair_price_repository.get_by_repair(
            db, repair_id=repair_id, skip=skip, limit=limit
        )

        # Получаем общее число цен для этого ремонта
        from sqlalchemy import select, func
        query = select(func.count()).where(
            self.repair_price_repository.model.repair_id == repair_id
        ).select_from(self.repair_price_repository.model)

        result = await db.execute(query)
        total = result.scalar_one()

        return repair_prices, total

    async def get_repair_price_statistics(
            self, db: AsyncSession, repair_id: Optional[int] = None, device_model_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Получить статистику цен на ремонт"""
        return await self.repair_price_repository.get_price_statistics(
            db, repair_id=repair_id, device_model_id=device_model_id
        )

    async def create_repair_price(self, db: AsyncSession, repair_price_in: RepairPriceCreate) -> RepairPrice:
        """Создать новую цену на ремонт"""
        # Проверяем, существует ли уже цена для этой модели и ремонта
        existing_price = await self.repair_price_repository.get_by_model_and_repair(
            db, device_model_id=repair_price_in.device_model_id, repair_id=repair_price_in.repair_id
        )

        if existing_price:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Цена на этот ремонт для данной модели устройства уже существует"
            )

        # Проверяем существование связанных сущностей
        from app.services.repair_service import repair_service
        from app.services.device_service import device_service

        # Проверка существования модели устройства
        await device_service.get_model(db, repair_price_in.device_model_id)

        # Проверка существования ремонта
        await repair_service.get_repair(db, repair_price_in.repair_id)

        return await self.repair_price_repository.create(db, obj_in=repair_price_in)

    async def update_repair_price(
            self, db: AsyncSession, repair_price_id: int, repair_price_in: RepairPriceUpdate
    ) -> RepairPrice:
        """Обновить цену на ремонт"""
        repair_price = await self.get_repair_price(db, repair_price_id)

        # Если меняется модель или ремонт, проверяем уникальность
        if (repair_price_in.device_model_id and repair_price_in.device_model_id != repair_price.device_model_id) or \
                (repair_price_in.repair_id and repair_price_in.repair_id != repair_price.repair_id):

            device_model_id = repair_price_in.device_model_id or repair_price.device_model_id
            repair_id = repair_price_in.repair_id or repair_price.repair_id

            existing_price = await self.repair_price_repository.get_by_model_and_repair(
                db, device_model_id=device_model_id, repair_id=repair_id
            )

            if existing_price and existing_price.id != repair_price_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Цена на этот ремонт для данной модели устройства уже существует"
                )

            # Проверяем существование связанных сущностей
            from app.services.repair_service import repair_service
            from app.services.device_service import device_service

            if repair_price_in.device_model_id:
                await device_service.get_model(db, repair_price_in.device_model_id)

            if repair_price_in.repair_id:
                await repair_service.get_repair(db, repair_price_in.repair_id)

        return await self.repair_price_repository.update(db, db_obj=repair_price, obj_in=repair_price_in)

    async def delete_repair_price(self, db: AsyncSession, repair_price_id: int) -> RepairPrice:
        """Удалить цену на ремонт"""
        repair_price = await self.get_repair_price(db, repair_price_id)
        return await self.repair_price_repository.remove(db, id=repair_price_id)

    # -- Операции с Price (цена в конкретном сервисном центре) --

    async def get_price(self, db: AsyncSession, price_id: int) -> Price:
        """Получить цену по ID"""
        price = await self.price_repository.get(db, price_id)
        if not price:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Цена с ID {price_id} не найдена"
            )
        return price

    async def get_price_with_relations(self, db: AsyncSession, price_id: int) -> Price:
        """Получить цену с загрузкой связанных данных"""
        price = await self.price_repository.get_with_relations(db, price_id)
        if not price:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Цена с ID {price_id} не найдена"
            )
        return price

    async def get_prices_by_service_center(
            self, db: AsyncSession, service_center_id: int, skip: int = 0, limit: int = 100
    ) -> Tuple[List[Price], int]:
        """Получить все цены для сервисного центра"""
        prices = await self.price_repository.get_by_service_center(
            db, service_center_id=service_center_id, skip=skip, limit=limit
        )

        # Получаем общее число цен для этого сервисного центра
        from sqlalchemy import select, func
        query = select(func.count()).where(
            self.price_repository.model.service_center_id == service_center_id
        ).select_from(self.price_repository.model)

        result = await db.execute(query)
        total = result.scalar_one()

        return prices, total

    async def get_prices_by_model_and_repair(
            self, db: AsyncSession, device_model_id: int, repair_id: int, skip: int = 0, limit: int = 100
    ) -> Tuple[List[Price], int]:
        """Получить все цены для конкретной модели и типа ремонта"""
        prices = await self.price_repository.get_by_model_and_repair(
            db, device_model_id=device_model_id, repair_id=repair_id, skip=skip, limit=limit
        )

        # Получаем общее число цен для этой модели и ремонта
        # Сначала получаем repair_price_id
        repair_price = await self.repair_price_repository.get_by_model_and_repair(
            db, device_model_id=device_model_id, repair_id=repair_id
        )

        if not repair_price:
            return [], 0

        from sqlalchemy import select, func
        query = select(func.count()).where(
            self.price_repository.model.repair_price_id == repair_price.id
        ).select_from(self.price_repository.model)

        result = await db.execute(query)
        total = result.scalar_one()

        return prices, total

    async def get_price_comparison(
            self, db: AsyncSession, device_model_id: int, repair_id: int
    ) -> Dict[str, Any]:
        """Получить сравнение цен на ремонт по всем сервисным центрам"""
        return await self.price_repository.get_price_comparison(
            db, device_model_id=device_model_id, repair_id=repair_id
        )

    async def create_price(self, db: AsyncSession, price_in: PriceCreate) -> Price:
        """Создать новую цену для сервисного центра"""
        # Проверяем, существует ли уже цена для этого сервисного центра и repair_price
        existing_price = await self.price_repository.get_by_service_center_and_repair_price(
            db, service_center_id=price_in.service_center_id, repair_price_id=price_in.repair_price_id
        )

        if existing_price:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Цена для этого сервисного центра и ремонта уже существует"
            )

        # Проверяем существование сервисного центра
        from app.services.service_center_service import service_center_service
        await service_center_service.get_service_center(db, price_in.service_center_id)

        # Проверяем существование repair_price
        await self.get_repair_price(db, price_in.repair_price_id)

        return await self.price_repository.create(db, obj_in=price_in)

    async def update_price(
            self, db: AsyncSession, price_id: int, price_in: PriceUpdate
    ) -> Price:
        """Обновить цену для сервисного центра"""
        price = await self.get_price(db, price_id)

        # Если меняется сервисный центр или repair_price, проверяем уникальность
        if (price_in.service_center_id and price_in.service_center_id != price.service_center_id) or \
                (price_in.repair_price_id and price_in.repair_price_id != price.repair_price_id):

            service_center_id = price_in.service_center_id or price.service_center_id
            repair_price_id = price_in.repair_price_id or price.repair_price_id

            existing_price = await self.price_repository.get_by_service_center_and_repair_price(
                db, service_center_id=service_center_id, repair_price_id=repair_price_id
            )

            if existing_price and existing_price.id != price_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Цена для этого сервисного центра и ремонта уже существует"
                )

            # Проверяем существование связанных сущностей
            from app.services.service_center_service import service_center_service

            if price_in.service_center_id:
                await service_center_service.get_service_center(db, price_in.service_center_id)

            if price_in.repair_price_id:
                await self.get_repair_price(db, price_in.repair_price_id)

        return await self.price_repository.update(db, db_obj=price, obj_in=price_in)

    async def delete_price(self, db: AsyncSession, price_id: int) -> Price:
        """Удалить цену"""
        price = await self.get_price(db, price_id)
        return await self.price_repository.remove(db, id=price_id)


# Экспортируем экземпляр сервиса для использования в API
price_service = PriceService()