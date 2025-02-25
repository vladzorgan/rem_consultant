"""Add Prestigio models

Revision ID: 50ed2a12bc64
Revises: 07e5de584707
Create Date: 2025-02-24 15:19:49.933667

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import column, table

# revision identifiers, used by Alembic.
revision: str = '50ed2a12bc64'
down_revision: Union[str, None] = '07e5de584707'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Определяем таблицу device_brands для поиска бренда
    device_brands = table('device_brands',
                          column('id', sa.Integer),
                          column('name', sa.String)
                          )

    # Получаем ID бренда Prestigio
    brand_name = 'Prestigio'  # Укажи здесь нужное название бренда вручную
    conn = op.get_bind()
    brand_id = conn.execute(
        sa.select(device_brands.c.id).where(device_brands.c.name == brand_name)
    ).scalar()

    if not brand_id:
        raise Exception(f"Бренд '{brand_name}' не найден в таблице device_brands")

    # Список моделей Prestigio для добавления
    device_models = [
        {"name": "Muze C7 LTE", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Grace M5 LTE", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "MUZE G7 LTE", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Wize Q3", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Muze X5 LTE", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "MUZE B3", "type": "smartphone", "device_brand_id": brand_id},
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
    # Удаляем все добавленные модели для Prestigio
    op.execute(
        "DELETE FROM device_models WHERE device_brand_id = (SELECT id FROM device_brands WHERE name = 'Prestigio')")
