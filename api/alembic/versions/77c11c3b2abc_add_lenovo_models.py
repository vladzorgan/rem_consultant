"""Add Lenovo models

Revision ID: 77c11c3b2abc
Revises: b1c4dfcd69c1
Create Date: 2025-02-24 15:08:52.615907

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import column, table

# revision identifiers, used by Alembic.
revision: str = '77c11c3b2abc'
down_revision: Union[str, None] = 'b1c4dfcd69c1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Определяем таблицу device_brands для поиска бренда
    device_brands = table('device_brands',
                          column('id', sa.Integer),
                          column('name', sa.String)
                          )

    # Получаем ID бренда Lenovo
    brand_name = 'Lenovo'  # Укажи здесь нужное название бренда вручную
    conn = op.get_bind()
    brand_id = conn.execute(
        sa.select(device_brands.c.id).where(device_brands.c.name == brand_name)
    ).scalar()

    if not brand_id:
        raise Exception(f"Бренд '{brand_name}' не найден в таблице device_brands")

    # Список моделей Lenovo для добавления
    device_models = [
        {"name": "K12 Pro", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Vibe Z2", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "K910 Vibe Z", "type": "smartphone", "device_brand_id": brand_id},
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
    # Удаляем все добавленные модели для Lenovo
    op.execute("DELETE FROM device_models WHERE device_brand_id = (SELECT id FROM device_brands WHERE name = 'Lenovo')")
