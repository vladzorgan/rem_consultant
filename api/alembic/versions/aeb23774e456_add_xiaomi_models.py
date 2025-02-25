"""Add Xiaomi models

Revision ID: aeb23774e456
Revises: e12b5db28b58
Create Date: 2025-02-24 15:00:11.333638

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import column, table

# revision identifiers, used by Alembic.
revision: str = 'aeb23774e456'
down_revision: Union[str, None] = 'e12b5db28b58'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    device_brands = table('device_brands',
                          column('id', sa.Integer),
                          column('name', sa.String)
                          )

    # Получаем ID бренда Xiaomi
    brand_name = 'Xiaomi'  # Укажи здесь нужное название бренда вручную
    conn = op.get_bind()
    brand_id = conn.execute(
        sa.select(device_brands.c.id).where(device_brands.c.name == brand_name)
    ).scalar()

    if not brand_id:
        raise Exception(f"Бренд '{brand_name}' не найден в таблице device_brands")

    # Список моделей Xiaomi для добавления
    device_models = [
        {"name": "Mi 11 Pro", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "12X", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "13 Pro", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Redmi 10", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Redmi 10c", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Redmi 12c", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Redmi 12", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Redmi Note 10S", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Redmi Note 11", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Redmi Note 11 Pro", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Redmi Note 11S", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Redmi Note 12", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Redmi Note 12S", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Poco F3", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Poco M3", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Poco X3 Pro", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Redmi Note 12 Pro", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Poco X3", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Poco M4 Pro", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Poco X5", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Mi 8 Lite", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Mi 9", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Mi 8 Pro", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Black Shark", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Mi Note 10 Lite", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "MI 9T", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Redmi 5", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Poco X5 Pro", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Mi Note 2", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Redmi Note 4X", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Mi 9 SE", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Mi 8 Explorer", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Redmi 8", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Redmi 9A", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "13 Lite", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Redmi Note 5 Pro", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Redmi Note 4", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Mi 11 Ultra", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "13", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Mi 11 Lite 5G", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Mi 10T Lite", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Mi 8", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "MI 9T Pro", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Mi Note 10 Pro", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Redmi 7", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Redmi 9", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Redmi Note 8", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Redmi Note 10", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Redmi Note 9", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Redmi Note 8T", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "11T Pro", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Mi 11", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Redmi Note 9 Pro", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "12", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Mi 10S", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "12 Pro", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Mi Note 3", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Mi 9 Lite", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Redmi Note 9S", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Redmi 9C", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Mi 11 Lite", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Redmi Note 7", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Mi 9 Pro", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Black Shark 4", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "11 Lite NE", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Redmi Note 8 Pro", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Redmi Note 10 Pro", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Redmi Note 6", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Mi 10", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Redmi Note 9T", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Mi 10T", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Redmi 9T", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Mi 10T Pro", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "11T", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Redmi 7a", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Mi A3", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Mi Note 10", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Redmi 5 Plus", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Redmi Note 5", "type": "smartphone", "device_brand_id": brand_id},
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
    # Удаляем все добавленные модели для Xiaomi
    op.execute("DELETE FROM device_models WHERE device_brand_id = (SELECT id FROM device_brands WHERE name = 'Xiaomi')")
