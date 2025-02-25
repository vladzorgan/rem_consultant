"""Add Blackview models

Revision ID: ac7e95db4eaf
Revises: 5d93ff93778f
Create Date: 2025-02-24 15:04:48.869416

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import column, table

# revision identifiers, used by Alembic.
revision: str = 'ac7e95db4eaf'
down_revision: Union[str, None] = '5d93ff93778f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    device_brands = table('device_brands',
                          column('id', sa.Integer),
                          column('name', sa.String)
                          )

    # Получаем ID бренда Blackview
    brand_name = 'Blackview'  # Укажи здесь нужное название бренда вручную
    conn = op.get_bind()
    brand_id = conn.execute(
        sa.select(device_brands.c.id).where(device_brands.c.name == brand_name)
    ).scalar()

    if not brand_id:
        raise Exception(f"Бренд '{brand_name}' не найден в таблице device_brands")

    # Список моделей Blackview для добавления
    device_models = [
        {"name": "BV5900", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "BV9900 Pro", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "A60", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "BL6000 Pro", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "P10000 Pro", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "BV9800 Pro", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "BV9600 Pro", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "BV6900", "type": "smartphone", "device_brand_id": brand_id},
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
    # Удаляем все добавленные модели для Blackview
    op.execute(
        "DELETE FROM device_models WHERE device_brand_id = (SELECT id FROM device_brands WHERE name = 'Blackview')")
