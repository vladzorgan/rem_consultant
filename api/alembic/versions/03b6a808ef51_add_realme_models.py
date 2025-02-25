"""Add Realme models

Revision ID: 03b6a808ef51
Revises: 50ed2a12bc64
Create Date: 2025-02-24 15:22:01.764115

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import column, table

# revision identifiers, used by Alembic.
revision: str = '03b6a808ef51'
down_revision: Union[str, None] = '50ed2a12bc64'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Определяем таблицу device_brands для поиска бренда
    device_brands = table('device_brands',
                          column('id', sa.Integer),
                          column('name', sa.String)
                          )

    # Получаем ID бренда Realme
    brand_name = 'Realme'  # Укажи здесь нужное название бренда вручную
    conn = op.get_bind()
    brand_id = conn.execute(
        sa.select(device_brands.c.id).where(device_brands.c.name == brand_name)
    ).scalar()

    if not brand_id:
        raise Exception(f"Бренд '{brand_name}' не найден в таблице device_brands")

    # Список моделей Realme для добавления
    device_models = [
        {"name": "GT NEO", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Narzo 30", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "C25S", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "GT Master Explorer Edition", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Narzo 50a", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "9 Pro", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "10 Pro Plus", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "10 Pro", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "C2", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "X", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "5", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "X2", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "3", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "6s", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "C3", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "7", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "C11", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "8 Pro", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "9", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "XT", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "GT", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "8 5G", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "7 pro", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "6 Pro", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "3 Pro", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "6", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "6i", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "8", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "8i", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "9 Pro Plus", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "9i", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "C15", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "C25", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "C21Y", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "GT Master Edition", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "GT Neo 2T", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "GT Neo2", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Q3s", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "X2 Pro", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "X3 SuperZoom", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "C21", "type": "smartphone", "device_brand_id": brand_id},
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
    # Удаляем все добавленные модели для Realme
    op.execute("DELETE FROM device_models WHERE device_brand_id = (SELECT id FROM device_brands WHERE name = 'Realme')")
