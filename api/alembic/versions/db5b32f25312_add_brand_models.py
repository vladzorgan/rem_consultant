"""Add Brand models

Revision ID: db5b32f25312
Revises: 989c0c923ba7
Create Date: 2025-02-24 14:51:18.176887

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import table, column

# revision identifiers, used by Alembic.
revision: str = 'db5b32f25312'
down_revision: Union[str, None] = '989c0c923ba7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Определяем таблицу device_brands для поиска бренда
    device_brands = table('device_brands',
                          column('id', sa.Integer),
                          column('name', sa.String)
                          )

    # Получаем ID бренда Apple (предполагаем, что бренд уже существует)
    brand_name = 'Apple'  # Укажи здесь нужное название бренда вручную
    conn = op.get_bind()
    brand_id = conn.execute(
        sa.select(device_brands.c.id).where(device_brands.c.name == brand_name)
    ).scalar()

    if not brand_id:
        raise Exception(f"Бренд '{brand_name}' не найден в таблице device_brands")

    # Список моделей для добавления
    device_models = [
        {"name": "iPhone 12 Pro", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "iPhone 12 Pro Max", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "iPhone 14 Plus", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "iPhone 15 Pro", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "iPhone 6 Plus", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "iPhone 11 Pro Max", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "iPhone 6s Plus", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "iPhone 12", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "iPhone 13 mini", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "iPhone 15 Pro Max", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "iPhone 5", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "iPhone 7", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "iPhone XS Max", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "iPhone XR", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "iPhone SE 2", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "iPhone 13 Pro", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "iPhone 14 Pro", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "iPhone 14 Pro Max", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "iPhone 16 Plus", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "iPhone 16", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "iPhone 16 Pro", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "iPhone 16 Pro Max", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "iPhone 6s", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "iPhone 6", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "iPhone 12 mini", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "iPhone 8 Plus", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "iPhone 11 Pro", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "iPhone SE", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "iPhone 11", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "iPhone 14", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "iPhone XS", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "iPhone 8", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "iPhone X", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "iPhone 15", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "iPhone 15 Plus", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "iPhone 13", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "iPhone 5s", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "iPhone 7 Plus", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "iPhone 13 Pro Max", "type": "smartphone", "device_brand_id": brand_id},
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
    # Удаляем все добавленные модели (без точного фильтра, так как это откат)
    op.execute("DELETE FROM device_models WHERE device_brand_id = (SELECT id FROM device_brands WHERE name = 'Apple')")
