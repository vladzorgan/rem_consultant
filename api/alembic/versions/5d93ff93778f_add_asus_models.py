"""Add ASUS models

Revision ID: 5d93ff93778f
Revises: 70bc9a1a6fe7
Create Date: 2025-02-24 15:03:31.610134

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import column, table

# revision identifiers, used by Alembic.
revision: str = '5d93ff93778f'
down_revision: Union[str, None] = '70bc9a1a6fe7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Определяем таблицу device_brands для поиска бренда
    device_brands = table('device_brands',
                          column('id', sa.Integer),
                          column('name', sa.String)
                          )

    # Получаем ID бренда ASUS
    brand_name = 'ASUS'  # Укажи здесь нужное название бренда вручную
    conn = op.get_bind()
    brand_id = conn.execute(
        sa.select(device_brands.c.id).where(device_brands.c.name == brand_name)
    ).scalar()

    if not brand_id:
        raise Exception(f"Бренд '{brand_name}' не найден в таблице device_brands")

    # Список моделей ASUS для добавления
    device_models = [
        {"name": "ROG Phone 3", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Zenfone 8", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "ROG Phone 5", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Zenfone 7", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "ZenFone 8 Flip", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Zenfone 6", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "ZenFone 7 Pro", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Zenfone Go ZB500KL", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "ROG Phone 5s", "type": "smartphone", "device_brand_id": brand_id},
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
    # Удаляем все добавленные модели для ASUS
    op.execute("DELETE FROM device_models WHERE device_brand_id = (SELECT id FROM device_brands WHERE name = 'ASUS')")
