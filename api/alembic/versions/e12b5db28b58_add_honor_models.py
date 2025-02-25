"""Add Honor models

Revision ID: e12b5db28b58
Revises: 5884235a8886
Create Date: 2025-02-24 14:57:53.598464

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import column, table

# revision identifiers, used by Alembic.
revision: str = 'e12b5db28b58'
down_revision: Union[str, None] = '5884235a8886'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    device_brands = table('device_brands',
                          column('id', sa.Integer),
                          column('name', sa.String)
                          )

    # Получаем ID бренда Honor
    brand_name = 'Honor'  # Укажи здесь нужное название бренда вручную
    conn = op.get_bind()
    brand_id = conn.execute(
        sa.select(device_brands.c.id).where(device_brands.c.name == brand_name)
    ).scalar()

    if not brand_id:
        raise Exception(f"Бренд '{brand_name}' не найден в таблице device_brands")

    # Список моделей Honor для добавления
    device_models = [
        {"name": "8C", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "70 Pro", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "6", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "X7", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "6X", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "8 Lite", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "9 Lite", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "20", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "20 Pro", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "9A", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "9X", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "70 Pro Plus", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "X9a", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "6C", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "8", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "7C", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "10", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "30i", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "9S", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "30 Pro Plus", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "8S", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "10 Premium", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "20I", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "7S", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "50 lite", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "View 20", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "8A Pro", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "70", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "30S", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "20S", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "7", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "7A", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "7A Pro", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "7X", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "9C", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "8X", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "20E", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "20 Lite", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "30", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "X8", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "5X", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "8A", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "10i", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "50", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "8 Pro", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "6C Pro", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "30 Pro", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "8X Max", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "10 Lite", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "7C Pro", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "10x Lite", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "9", "type": "smartphone", "device_brand_id": brand_id},
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
    # Удаляем все добавленные модели для Honor
    op.execute("DELETE FROM device_models WHERE device_brand_id = (SELECT id FROM device_brands WHERE name = 'Honor')")
