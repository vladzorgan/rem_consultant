"""Add Motorola models

Revision ID: 079453741b9f
Revises: 77c11c3b2abc
Create Date: 2025-02-24 15:10:47.105509

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import column, table

# revision identifiers, used by Alembic.
revision: str = '079453741b9f'
down_revision: Union[str, None] = '77c11c3b2abc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Определяем таблицу device_brands для поиска бренда
    device_brands = table('device_brands',
                          column('id', sa.Integer),
                          column('name', sa.String)
                          )

    # Получаем ID бренда Motorola
    brand_name = 'Motorola'  # Укажи здесь нужное название бренда вручную
    conn = op.get_bind()
    brand_id = conn.execute(
        sa.select(device_brands.c.id).where(device_brands.c.name == brand_name)
    ).scalar()

    if not brand_id:
        raise Exception(f"Бренд '{brand_name}' не найден в таблице device_brands")

    # Список моделей Motorola для добавления
    device_models = [
        {"name": "Edge 20", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Edge S", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Moto Z Play", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "One Power", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "One Hyper", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "One Zoom", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Moto Z4", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Moto G7 Plus", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Edge+", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Moto E7 Plus", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "G8", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Edge X30", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Edge 20 Pro", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "G9 Play", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "G8 Power", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Moto G7", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Moto G 5G Plus", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Moto G9 Plus", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "One Action", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "One Fusion+", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "G8 Plus", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "One Vision", "type": "smartphone", "device_brand_id": brand_id},
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
    # Удаляем все добавленные модели для Motorola
    op.execute(
        "DELETE FROM device_models WHERE device_brand_id = (SELECT id FROM device_brands WHERE name = 'Motorola')")
