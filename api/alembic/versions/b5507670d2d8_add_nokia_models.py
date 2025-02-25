"""Add Nokia models

Revision ID: b5507670d2d8
Revises: 079453741b9f
Create Date: 2025-02-24 15:13:20.365899

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import column, table

# revision identifiers, used by Alembic.
revision: str = 'b5507670d2d8'
down_revision: Union[str, None] = '079453741b9f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Определяем таблицу device_brands для поиска бренда
    device_brands = table('device_brands',
                          column('id', sa.Integer),
                          column('name', sa.String)
                          )

    # Получаем ID бренда Nokia
    brand_name = 'Nokia'  # Укажи здесь нужное название бренда вручную
    conn = op.get_bind()
    brand_id = conn.execute(
        sa.select(device_brands.c.id).where(device_brands.c.name == brand_name)
    ).scalar()

    if not brand_id:
        raise Exception(f"Бренд '{brand_name}' не найден в таблице device_brands")

    # Список моделей Nokia для добавления
    device_models = [
        {"name": "G10", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "7", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "6.1", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "5.4", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "XR20", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "8.3 5G", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "G20", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "X10", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "5.1", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "G21", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "7.2", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "C3", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "5.3", "type": "smartphone", "device_brand_id": brand_id},
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
    # Удаляем все добавленные модели для Nokia
    op.execute("DELETE FROM device_models WHERE device_brand_id = (SELECT id FROM device_brands WHERE name = 'Nokia')")
