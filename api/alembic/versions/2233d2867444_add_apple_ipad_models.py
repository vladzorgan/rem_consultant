"""Add Apple iPad models

Revision ID: 2233d2867444
Revises: 33552ee63981
Create Date: 2025-02-24 15:34:56.067425

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import column, table

# revision identifiers, used by Alembic.
revision: str = '2233d2867444'
down_revision: Union[str, None] = '33552ee63981'
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

    # Список моделей iPad для добавления
    device_models = [
        {"name": "iPad Air 5", "type": "tablet", "device_brand_id": brand_id},
        {"name": "iPad Air 4", "type": "tablet", "device_brand_id": brand_id},
        {"name": "iPad Air 3", "type": "tablet", "device_brand_id": brand_id},
        {"name": "iPad Air 2", "type": "tablet", "device_brand_id": brand_id},
        {"name": "iPad Air", "type": "tablet", "device_brand_id": brand_id},
        {"name": "iPad mini 6", "type": "tablet", "device_brand_id": brand_id},
        {"name": "iPad mini 5", "type": "tablet", "device_brand_id": brand_id},
        {"name": "iPad mini 4", "type": "tablet", "device_brand_id": brand_id},
        {"name": "iPad mini 3", "type": "tablet", "device_brand_id": brand_id},
        {"name": "iPad mini 2", "type": "tablet", "device_brand_id": brand_id},
        {"name": "iPad mini", "type": "tablet", "device_brand_id": brand_id},
        {"name": "iPad Pro 12.9 (2022)", "type": "tablet", "device_brand_id": brand_id},
        {"name": "iPad Pro 11 (2022)", "type": "tablet", "device_brand_id": brand_id},
        {"name": "iPad Pro 12.9 (2021)", "type": "tablet", "device_brand_id": brand_id},
        {"name": "iPad Pro 11 (2021)", "type": "tablet", "device_brand_id": brand_id},
        {"name": "iPad Pro 12.9 (2020)", "type": "tablet", "device_brand_id": brand_id},
        {"name": "iPad Pro 11 (2020)", "type": "tablet", "device_brand_id": brand_id},
        {"name": "iPad Pro 12.9 (2018)", "type": "tablet", "device_brand_id": brand_id},
        {"name": "iPad Pro 11 (2018)", "type": "tablet", "device_brand_id": brand_id},
        {"name": "iPad Pro 9.7", "type": "tablet", "device_brand_id": brand_id},
        {"name": "iPad Pro 10.5", "type": "tablet", "device_brand_id": brand_id},
        {"name": "iPad Pro 12.9 (2017)", "type": "tablet", "device_brand_id": brand_id},
        {"name": "iPad 10", "type": "tablet", "device_brand_id": brand_id},
        {"name": "iPad 9", "type": "tablet", "device_brand_id": brand_id},
        {"name": "iPad 8", "type": "tablet", "device_brand_id": brand_id},
        {"name": "iPad 7", "type": "tablet", "device_brand_id": brand_id},
        {"name": "iPad 6", "type": "tablet", "device_brand_id": brand_id},
        {"name": "iPad 5", "type": "tablet", "device_brand_id": brand_id},
        {"name": "iPad 4", "type": "tablet", "device_brand_id": brand_id},
        {"name": "iPad 3", "type": "tablet", "device_brand_id": brand_id},
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
    # Удаляем все добавленные модели для Apple (только планшеты)
    op.execute(
        "DELETE FROM device_models WHERE device_brand_id = (SELECT id FROM device_brands WHERE name = 'Apple') AND type = 'tablet'")
