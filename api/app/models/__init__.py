# импорт всех моделей из модулей
from app.models.location import Region, City
from app.models.user import User
from app.models.service import (
    ServiceCenter, AddServiceRequest, ServiceCenterAddress,
    ServiceCenterLink, Review
)
from app.models.device import DeviceBrand, DeviceModel
from app.models.repair import (
    Repair, RepairType, ModelRepair, Part, RepairPart,
    RepairPrice, Price, PriceAnalytic
)
from app.models.logging import BotLog, ApiLog

# Импорт перечислений
from app.models.common import RequestStatus, DeviceType, LinkType

# Создать все таблицы при импорте (только для разработки)
# В продакшене используйте Alembic
# init_db()

__all__ = [
    # Местоположения
    'Region', 'City',

    # Пользователи
    'User',

    # Сервисные центры
    'ServiceCenter', 'AddServiceRequest', 'ServiceCenterAddress', 'ServiceCenterLink', 'Review',

    # Устройства
    'DeviceBrand', 'DeviceModel',

    # Ремонты
    'Repair', 'RepairType', 'ModelRepair', 'Part', 'RepairPart', 'RepairPrice', 'Price', 'PriceAnalytic',

    # Логи
    'BotLog', 'ApiLog',

    # Перечисления
    'RequestStatus', 'DeviceType', 'LinkType',
]