"""Add Meizu models

Revision ID: 70bc9a1a6fe7
Revises: 3e3d2aea09e3
Create Date: 2025-02-24 15:02:47.702442

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import column, table

# revision identifiers, used by Alembic.
revision: str = '70bc9a1a6fe7'
down_revision: Union[str, None] = '3e3d2aea09e3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    device_brands = table('device_brands',
                          column('id', sa.Integer),
                          column('name', sa.String)
                          )

    # Получаем ID бренда Meizu
    brand_name = 'Meizu'  # Укажи здесь нужное название бренда вручную
    conn = op.get_bind()
    brand_id = conn.execute(
        sa.select(device_brands.c.id).where(device_brands.c.name == brand_name)
    ).scalar()

    if not brand_id:
        raise Exception(f"Бренд '{brand_name}' не найден в таблице device_brands")

    # Список моделей Meizu для добавления
    device_models = [
        {"name": "E2", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "M2 mini", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "MX2", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "M2 Note", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "16xs", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Pro 6s", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "16th", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "16s", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Pro 6", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "16 Plus", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "MX4", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "MX5", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "M8c", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "M3 Max", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Note 9", "type": "smartphone", "device_brand_id": brand_id},
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
    # Удаляем все добавленные модели для Meizu
    op.execute("DELETE FROM device_models WHERE device_brand_id = (SELECT id FROM device_brands WHERE name = 'Meizu')")
