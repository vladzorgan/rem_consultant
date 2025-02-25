from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy import select, func, desc, and_, or_, between
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from app.models.repair import (
    Repair, RepairType, Part, RepairPart, ModelRepair,
    RepairPrice, Price, PriceAnalytic
)
from app.schemas.repair import (
    RepairCreate, RepairUpdate, RepairTypeCreate, RepairTypeUpdate,
    PartCreate, PartUpdate, RepairPartCreate, RepairPartUpdate,
    ModelRepairCreate, ModelRepairUpdate, RepairPriceCreate, RepairPriceUpdate,
    PriceCreate, PriceUpdate
)
from app.repositories.base import BaseRepository


class RepairRepository(BaseRepository[Repair, RepairCreate, RepairUpdate]):
    def __init__(self):
        super().__init__(Repair)

    async def get_with_types(self, db: AsyncSession, id: int) -> Optional[Repair]:
        """
        Получить ремонт с загрузкой связанных типов ремонта
        """
        query = select(Repair).where(Repair.id == id).options(selectinload(Repair.repair_types))
        result = await db.execute(query)
        return result.scalars().first()

    async def get_by_name(self, db: AsyncSession, name: str) -> Optional[Repair]:
        """
        Поиск ремонта по имени
        """
        query = select(Repair).where(func.lower(Repair.name) == func.lower(name))
        result = await db.execute(query)
        return result.scalars().first()

    async def search(
            self, db: AsyncSession, *, keyword: str, skip: int = 0, limit: int = 100
    ) -> List[Repair]:
        """
        Поиск ремонтов по ключевому слову
        """
        query = (
            select(Repair)
            .where(
                or_(
                    func.lower(Repair.name).contains(func.lower(keyword)),
                    func.lower(Repair.description).contains(func.lower(keyword))
                )
            )
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        return result.scalars().all()


class RepairTypeRepository(BaseRepository[RepairType, RepairTypeCreate, RepairTypeUpdate]):
    def __init__(self):
        super().__init__(RepairType)

    async def get_with_repair_parts(self, db: AsyncSession, id: int) -> Optional[RepairType]:
        """
        Получить тип ремонта с загрузкой связанных запчастей
        """
        query = select(RepairType).where(RepairType.id == id).options(
            selectinload(RepairType.repair_parts).selectinload(RepairPart.part)
        )
        result = await db.execute(query)
        return result.scalars().first()

    async def get_by_name(
            self, db: AsyncSession, name: str, group_name: Optional[str] = None
    ) -> Optional[RepairType]:
        """
        Поиск типа ремонта по имени и опционально по группе
        """
        conditions = [func.lower(RepairType.name) == func.lower(name)]

        if group_name:
            conditions.append(func.lower(RepairType.group_name) == func.lower(group_name))

        query = select(RepairType).where(and_(*conditions))
        result = await db.execute(query)
        return result.scalars().first()

    async def search(
            self, db: AsyncSession, *, keyword: str, group_name: Optional[str] = None,
            skip: int = 0, limit: int = 100
    ) -> List[RepairType]:
        """
        Поиск типов ремонта по ключевому слову и опционально по группе
        """
        conditions = [
            or_(
                func.lower(RepairType.name).contains(func.lower(keyword)),
                func.lower(RepairType.description).contains(func.lower(keyword))
            )
        ]

        if group_name:
            conditions.append(func.lower(RepairType.group_name) == func.lower(group_name))

        query = (
            select(RepairType)
            .where(and_(*conditions))
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        return result.scalars().all()

    async def get_by_group(
            self, db: AsyncSession, *, group_name: str, skip: int = 0, limit: int = 100
    ) -> List[RepairType]:
        """
        Получить типы ремонта по группе
        """
        query = (
            select(RepairType)
            .where(func.lower(RepairType.group_name) == func.lower(group_name))
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        return result.scalars().all()


class PartRepository(BaseRepository[Part, PartCreate, PartUpdate]):
    def __init__(self):
        super().__init__(Part)

    async def get_by_sku(self, db: AsyncSession, sku: str) -> Optional[Part]:
        """
        Получить запчасть по артикулу (SKU)
        """
        query = select(Part).where(func.lower(Part.sku) == func.lower(sku))
        result = await db.execute(query)
        return result.scalars().first()

    async def search(
            self, db: AsyncSession, *, keyword: str, skip: int = 0, limit: int = 100
    ) -> List[Part]:
        """
        Поиск запчастей по ключевому слову
        """
        query = (
            select(Part)
            .where(
                or_(
                    func.lower(Part.name).contains(func.lower(keyword)),
                    func.lower(Part.description).contains(func.lower(keyword)),
                    func.lower(Part.sku).contains(func.lower(keyword)),
                    func.lower(Part.manufacturer).contains(func.lower(keyword))
                )
            )
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        return result.scalars().all()

    async def get_by_price_range(
            self, db: AsyncSession, *, min_price: float = 0, max_price: Optional[float] = None,
            skip: int = 0, limit: int = 100
    ) -> List[Part]:
        """
        Получить запчасти в заданном диапазоне цен
        """
        conditions = [Part.retail_price >= min_price]

        if max_price is not None:
            conditions.append(Part.retail_price <= max_price)

        query = (
            select(Part)
            .where(and_(*conditions))
            .order_by(Part.retail_price)
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        return result.scalars().all()


class RepairPartRepository(BaseRepository[RepairPart, RepairPartCreate, RepairPartUpdate]):
    def __init__(self):
        super().__init__(RepairPart)

    async def get_with_part(self, db: AsyncSession, id: int) -> Optional[RepairPart]:
        """
        Получить связь ремонт-запчасть с данными о запчасти
        """
        query = select(RepairPart).where(RepairPart.id == id).options(joinedload(RepairPart.part))
        result = await db.execute(query)
        return result.scalars().first()

    async def get_by_repair_type_and_part(
            self, db: AsyncSession, *, repair_type_id: int, part_id: int
    ) -> Optional[RepairPart]:
        """
        Получить связь по ID типа ремонта и ID запчасти
        """
        query = select(RepairPart).where(
            and_(
                RepairPart.repair_type_id == repair_type_id,
                RepairPart.part_id == part_id
            )
        )
        result = await db.execute(query)
        return result.scalars().first()

    async def get_by_repair_type(
            self, db: AsyncSession, *, repair_type_id: int, skip: int = 0, limit: int = 100
    ) -> List[RepairPart]:
        """
        Получить все запчасти для типа ремонта
        """
        query = (
            select(RepairPart)
            .where(RepairPart.repair_type_id == repair_type_id)
            .options(joinedload(RepairPart.part))
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        return result.scalars().all()


class ModelRepairRepository(BaseRepository[ModelRepair, ModelRepairCreate, ModelRepairUpdate]):
    def __init__(self):
        super().__init__(ModelRepair)

    async def get_with_relations(self, db: AsyncSession, id: int) -> Optional[ModelRepair]:
        """
        Получить связь модель-ремонт с загрузкой связанных данных
        """
        query = select(ModelRepair).where(ModelRepair.id == id).options(
            joinedload(ModelRepair.model),
            joinedload(ModelRepair.repair_type)
        )
        result = await db.execute(query)
        return result.scalars().first()

    async def get_by_model(
            self, db: AsyncSession, *, model_id: int, skip: int = 0, limit: int = 100
    ) -> List[ModelRepair]:
        """
        Получить все типы ремонта для модели устройства
        """
        query = (
            select(ModelRepair)
            .where(ModelRepair.model_id == model_id)
            .options(joinedload(ModelRepair.repair_type))
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        return result.scalars().all()

    async def get_by_repair_type(
            self, db: AsyncSession, *, repair_type_id: int, skip: int = 0, limit: int = 100
    ) -> List[ModelRepair]:
        """
        Получить все модели для типа ремонта
        """
        query = (
            select(ModelRepair)
            .where(ModelRepair.repair_type_id == repair_type_id)
            .options(joinedload(ModelRepair.model))
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        return result.scalars().all()

    async def get_by_model_and_repair_type(
            self, db: AsyncSession, *, model_id: int, repair_type_id: int
    ) -> Optional[ModelRepair]:
        """
        Получить связь по ID модели и ID типа ремонта
        """
        query = select(ModelRepair).where(
            and_(
                ModelRepair.model_id == model_id,
                ModelRepair.repair_type_id == repair_type_id
            )
        )
        result = await db.execute(query)
        return result.scalars().first()


class RepairPriceRepository(BaseRepository[RepairPrice, RepairPriceCreate, RepairPriceUpdate]):
    def __init__(self):
        super().__init__(RepairPrice)

    async def get_with_relations(self, db: AsyncSession, id: int) -> Optional[RepairPrice]:
        """
        Получить цену на ремонт с загрузкой связанных данных
        """
        query = select(RepairPrice).where(RepairPrice.id == id).options(
            joinedload(RepairPrice.device_model),
            joinedload(RepairPrice.repair)
        )
        result = await db.execute(query)
        return result.scalars().first()

    async def get_by_model_and_repair(
            self, db: AsyncSession, *, device_model_id: int, repair_id: int
    ) -> Optional[RepairPrice]:
        """
        Получить цену по ID модели и ID ремонта
        """
        query = select(RepairPrice).where(
            and_(
                RepairPrice.device_model_id == device_model_id,
                RepairPrice.repair_id == repair_id
            )
        )
        result = await db.execute(query)
        return result.scalars().first()

    async def get_by_model(
            self, db: AsyncSession, *, device_model_id: int, skip: int = 0, limit: int = 100
    ) -> List[RepairPrice]:
        """
        Получить все цены на ремонт для модели устройства
        """
        query = (
            select(RepairPrice)
            .where(RepairPrice.device_model_id == device_model_id)
            .options(joinedload(RepairPrice.repair))
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        return result.scalars().all()

    async def get_by_repair(
            self, db: AsyncSession, *, repair_id: int, skip: int = 0, limit: int = 100
    ) -> List[RepairPrice]:
        """
        Получить все цены на ремонт для типа ремонта
        """
        query = (
            select(RepairPrice)
            .where(RepairPrice.repair_id == repair_id)
            .options(joinedload(RepairPrice.device_model))
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        return result.scalars().all()

    async def get_price_statistics(
            self, db: AsyncSession, *, repair_id: Optional[int] = None, device_model_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Получить статистику цен (среднюю, минимальную, максимальную)
        """
        conditions = []

        if repair_id is not None:
            conditions.append(RepairPrice.repair_id == repair_id)

        if device_model_id is not None:
            conditions.append(RepairPrice.device_model_id == device_model_id)

        query = select(
            func.avg(RepairPrice.price).label("avg_price"),
            func.min(RepairPrice.price).label("min_price"),
            func.max(RepairPrice.price).label("max_price"),
            func.count(RepairPrice.id).label("count")
        ).where(and_(*conditions))

        result = await db.execute(query)
        stats = result.fetchone()

        if not stats:
            return {
                "avg_price": 0,
                "min_price": 0,
                "max_price": 0,
                "count": 0
            }

        return {
            "avg_price": float(stats.avg_price) if stats.avg_price else 0,
            "min_price": float(stats.min_price) if stats.min_price else 0,
            "max_price": float(stats.max_price) if stats.max_price else 0,
            "count": stats.count
        }


class PriceRepository(BaseRepository[Price, PriceCreate, PriceUpdate]):
    def __init__(self):
        super().__init__(Price)

    async def get_with_relations(self, db: AsyncSession, id: int) -> Optional[Price]:
        """
        Получить цену с загрузкой связанных данных
        """
        query = select(Price).where(Price.id == id).options(
            joinedload(Price.service_center),
            joinedload(Price.repair_price).joinedload(RepairPrice.repair),
            joinedload(Price.repair_price).joinedload(RepairPrice.device_model)
        )
        result = await db.execute(query)
        return result.scalars().first()

    async def get_by_service_center_and_repair_price(
            self, db: AsyncSession, *, service_center_id: int, repair_price_id: int
    ) -> Optional[Price]:
        """
        Получить цену по ID сервисного центра и ID цены на ремонт
        """
        query = select(Price).where(
            and_(
                Price.service_center_id == service_center_id,
                Price.repair_price_id == repair_price_id
            )
        )
        result = await db.execute(query)
        return result.scalars().first()

    async def get_by_service_center(
            self, db: AsyncSession, *, service_center_id: int, skip: int = 0, limit: int = 100
    ) -> List[Price]:
        """
        Получить все цены для сервисного центра
        """
        query = (
            select(Price)
            .where(Price.service_center_id == service_center_id)
            .options(
                joinedload(Price.repair_price).joinedload(RepairPrice.repair),
                joinedload(Price.repair_price).joinedload(RepairPrice.device_model)
            )
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        return result.scalars().all()

    async def get_by_model_and_repair(
            self, db: AsyncSession, *, device_model_id: int, repair_id: int,
            skip: int = 0, limit: int = 100
    ) -> List[Price]:
        """
        Получить все цены для конкретной модели и типа ремонта
        """
        # Сначала получаем repair_price_id для заданной модели и ремонта
        subquery = select(RepairPrice.id).where(
            and_(
                RepairPrice.device_model_id == device_model_id,
                RepairPrice.repair_id == repair_id
            )
        ).scalar_subquery()

        query = (
            select(Price)
            .where(Price.repair_price_id == subquery)
            .options(joinedload(Price.service_center))
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        return result.scalars().all()

    async def get_price_comparison(
            self, db: AsyncSession, *, device_model_id: int, repair_id: int
    ) -> Dict[str, Any]:
        """
        Получить сравнение цен на ремонт по всем сервисным центрам
        """
        # Получаем repair_price_id для заданной модели и ремонта
        rp_query = select(RepairPrice.id).where(
            and_(
                RepairPrice.device_model_id == device_model_id,
                RepairPrice.repair_id == repair_id
            )
        )
        rp_result = await db.execute(rp_query)
        repair_price_id = rp_result.scalar_one_or_none()

        if not repair_price_id:
            return {
                "avg_price": 0,
                "min_price": 0,
                "max_price": 0,
                "count": 0,
                "service_centers": []
            }

        # Получаем статистику
        stats_query = select(
            func.avg(Price.price).label("avg_price"),
            func.min(Price.price).label("min_price"),
            func.max(Price.price).label("max_price"),
            func.count(Price.id).label("count")
        ).where(Price.repair_price_id == repair_price_id)

        stats_result = await db.execute(stats_query)
        stats = stats_result.fetchone()

        # Получаем список цен по сервисным центрам
        sc_query = (
            select(Price, Price.service_center_id.label("service_center_id"))
            .where(Price.repair_price_id == repair_price_id)
            .options(joinedload(Price.service_center))
            .order_by(Price.price)
        )

        sc_result = await db.execute(sc_query)
        prices = sc_result.unique().all()

        service_centers = [
            {
                "service_center_id": price.service_center_id,
                "service_center_name": price.service_center.name if price.service_center else None,
                "price": price.price
            }
            for price, _ in prices
        ]

        return {
            "avg_price": float(stats.avg_price) if stats.avg_price else 0,
            "min_price": float(stats.min_price) if stats.min_price else 0,
            "max_price": float(stats.max_price) if stats.max_price else 0,
            "count": stats.count,
            "service_centers": service_centers
        }