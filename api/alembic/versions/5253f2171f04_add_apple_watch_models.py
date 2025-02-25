"""Add Apple watch models

Revision ID: 5253f2171f04
Revises: 2233d2867444
Create Date: 2025-02-24 15:36:24.557313

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import column, table

# revision identifiers, used by Alembic.
revision: str = '5253f2171f04'
down_revision: Union[str, None] = '2233d2867444'
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

    # Список моделей Apple Watch для добавления
    device_models = [
        {"name": "Apple Watch Series 1", "type": "smartwatch", "device_brand_id": brand_id},
        {"name": "Apple Watch Series 2", "type": "smartwatch", "device_brand_id": brand_id},
        {"name": "Apple Watch Series 3", "type": "smartwatch", "device_brand_id": brand_id},
        {"name": "Apple Watch Series 4", "type": "smartwatch", "device_brand_id": brand_id},
        {"name": "Apple Watch Series 5", "type": "smartwatch", "device_brand_id": brand_id},
        {"name": "Apple Watch Series 6", "type": "smartwatch", "device_brand_id": brand_id},
        {"name": "Apple Watch Series 7", "type": "smartwatch", "device_brand_id": brand_id},
        {"name": "Apple Watch Series 8", "type": "smartwatch", "device_brand_id": brand_id},
        {"name": "Apple Watch Series 9", "type": "smartwatch", "device_brand_id": brand_id},
        {"name": "Apple Watch SE", "type": "smartwatch", "device_brand_id": brand_id},
        {"name": "Apple Watch SE 2", "type": "smartwatch", "device_brand_id": brand_id},
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
    op.execute("DELETE FROM device_models WHERE device_brand_id = (SELECT id FROM device_brands WHERE name = 'Apple')")
