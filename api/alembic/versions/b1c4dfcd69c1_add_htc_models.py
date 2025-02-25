"""Add HTC models

Revision ID: b1c4dfcd69c1
Revises: 3c9ff75e9e57
Create Date: 2025-02-24 15:07:32.690264

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import column, table

# revision identifiers, used by Alembic.
revision: str = 'b1c4dfcd69c1'
down_revision: Union[str, None] = '3c9ff75e9e57'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Определяем таблицу device_brands для поиска бренда
    device_brands = table('device_brands',
                          column('id', sa.Integer),
                          column('name', sa.String)
                          )

    # Получаем ID бренда HTC
    brand_name = 'HTC'  # Укажи здесь нужное название бренда вручную
    conn = op.get_bind()
    brand_id = conn.execute(
        sa.select(device_brands.c.id).where(device_brands.c.name == brand_name)
    ).scalar()

    if not brand_id:
        raise Exception(f"Бренд '{brand_name}' не найден в таблице device_brands")

    # Список моделей HTC для добавления
    device_models = [
        {"name": "Desire C", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Sensation", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Wildfire S", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "One M8", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Desire HD", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Butterfly S", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Evo 3d", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Wildfire E", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "One M7", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Desire 20 Pro", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Desire X", "type": "smartphone", "device_brand_id": brand_id},
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
    # Удаляем все добавленные модели для HTC
    op.execute("DELETE FROM device_models WHERE device_brand_id = (SELECT id FROM device_brands WHERE name = 'HTC')")
