"""Add Apple imac models

Revision ID: b4c82dddd48d
Revises: 37868437d2bd
Create Date: 2025-02-24 15:42:29.680692

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import column, table

# revision identifiers, used by Alembic.
revision: str = 'b4c82dddd48d'
down_revision: Union[str, None] = '37868437d2bd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Определяем таблицу device_brands для поиска бренда
    device_brands = table('device_brands',
                          column('id', sa.Integer),
                          column('name', sa.String)
                          )

    # Получаем ID бренда Apple
    brand_name = 'Apple'  # Укажи здесь нужное название бренда вручную
    conn = op.get_bind()
    brand_id = conn.execute(
        sa.select(device_brands.c.id).where(device_brands.c.name == brand_name)
    ).scalar()

    if not brand_id:
        raise Exception(f"Бренд '{brand_name}' не найден в таблице device_brands")

    # Список моделей iMac для добавления
    device_models = [
        {"name": "iMac 21.5, 2019", "type": "desktop", "device_brand_id": brand_id},
        {"name": "iMac 27, 2019", "type": "desktop", "device_brand_id": brand_id},
        {"name": "iMac 21.5, 2017", "type": "desktop", "device_brand_id": brand_id},
        {"name": "iMac Pro 2017", "type": "desktop", "device_brand_id": brand_id},
        {"name": "iMac Retina 4K, 21.5, 2017", "type": "desktop", "device_brand_id": brand_id},
        {"name": "iMac Retina 5K, 27, 2017", "type": "desktop", "device_brand_id": brand_id},
        {"name": "iMac Retina 5K, 27, (2017) A1419", "type": "desktop", "device_brand_id": brand_id},
        {"name": "iMac 21.5, Late 2015", "type": "desktop", "device_brand_id": brand_id},
        {"name": "iMac Retina 4K, 21.5, Late 2015", "type": "desktop", "device_brand_id": brand_id},
        {"name": "iMac Retina 5K, 27, Late 2015", "type": "desktop", "device_brand_id": brand_id},
        {"name": "iMac 21.5, Mid 2014", "type": "desktop", "device_brand_id": brand_id},
        {"name": "iMac Retina 5K, 27, Mid 2015", "type": "desktop", "device_brand_id": brand_id},
        {"name": "iMac Retina 5K, 27, Late 2014", "type": "desktop", "device_brand_id": brand_id},
        {"name": "iMac 21.5, Early 2013", "type": "desktop", "device_brand_id": brand_id},
        {"name": "iMac 21.5, Late 2013", "type": "desktop", "device_brand_id": brand_id},
        {"name": "iMac 27, 2013", "type": "desktop", "device_brand_id": brand_id},
        {"name": "iMac 27, Late 2013", "type": "desktop", "device_brand_id": brand_id},
        {"name": "iMac 21.5, Late 2012", "type": "desktop", "device_brand_id": brand_id},
        {"name": "iMac 21.5, Late 2012 A1418", "type": "desktop", "device_brand_id": brand_id},
        {"name": "iMac 27, Late 2012", "type": "desktop", "device_brand_id": brand_id},
        {"name": "iMac 27, Mid 2012 A1312", "type": "desktop", "device_brand_id": brand_id},
        {"name": "iMac 21.5, Late 2011", "type": "desktop", "device_brand_id": brand_id},
        {"name": "iMac 21.5, Mid 2011", "type": "desktop", "device_brand_id": brand_id},
        {"name": "iMac 21.5, Mid 2011 A1311", "type": "desktop", "device_brand_id": brand_id},
        {"name": "iMac 27 A1419 (2013)", "type": "desktop", "device_brand_id": brand_id},
        {"name": "iMac 27, Mid 2011", "type": "desktop", "device_brand_id": brand_id},
        {"name": "iMac 27, 2010", "type": "desktop", "device_brand_id": brand_id},
        {"name": "iMac Mid 2010 A1311", "type": "desktop", "device_brand_id": brand_id},
        {"name": "iMac Mid 2010 A1312", "type": "desktop", "device_brand_id": brand_id},
        {"name": "iMac 20, 2009", "type": "desktop", "device_brand_id": brand_id},
        {"name": "iMac 21.5, 2009", "type": "desktop", "device_brand_id": brand_id},
        {"name": "iMac 24, 2009", "type": "desktop", "device_brand_id": brand_id},
        {"name": "iMac 27, 2009", "type": "desktop", "device_brand_id": brand_id},
    ]

    # Вставляем модели в таблицу device_models
    op.bulk_insert(
        table('device_models',
              column('name', sa.String),
              column('type', sa.String),
              column('device_brand_id', sa.Integer),
              column('created_at', sa.DateTime),
              column('updated_at', sa.DateTime)
              ),
        device_models
    )


def downgrade():
    # Удаляем все добавленные модели для Apple
    op.execute("DELETE FROM device_models WHERE device_brand_id = (SELECT id FROM device_brands WHERE name = 'Apple' AND type = 'desktop')")
