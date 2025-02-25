"""Add Highscreen models

Revision ID: 3c9ff75e9e57
Revises: 44fdd2a44825
Create Date: 2025-02-24 15:06:57.916927

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import column, table

# revision identifiers, used by Alembic.
revision: str = '3c9ff75e9e57'
down_revision: Union[str, None] = '44fdd2a44825'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    device_brands = table('device_brands',
                          column('id', sa.Integer),
                          column('name', sa.String)
                          )

    # Получаем ID бренда Highscreen
    brand_name = 'Highscreen'  # Укажи здесь нужное название бренда вручную
    conn = op.get_bind()
    brand_id = conn.execute(
        sa.select(device_brands.c.id).where(device_brands.c.name == brand_name)
    ).scalar()

    if not brand_id:
        raise Exception(f"Бренд '{brand_name}' не найден в таблице device_brands")

    # Список моделей Highscreen для добавления
    device_models = [
        {"name": "Fest Pro", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Easy Power", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Fest XL", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Easy XL", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Fest", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Power Five Max 3", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Power Five Max 2", "type": "smartphone", "device_brand_id": brand_id},
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
    # Удаляем все добавленные модели для Highscreen
    op.execute(
        "DELETE FROM device_models WHERE device_brand_id = (SELECT id FROM device_brands WHERE name = 'Highscreen')")
