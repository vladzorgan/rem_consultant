"""Add ZTE models

Revision ID: 33552ee63981
Revises: 7766c804df6c
Create Date: 2025-02-24 15:27:21.928925

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import column, table

# revision identifiers, used by Alembic.
revision: str = '33552ee63981'
down_revision: Union[str, None] = '7766c804df6c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Определяем таблицу device_brands для поиска бренда
    device_brands = table('device_brands',
                          column('id', sa.Integer),
                          column('name', sa.String)
                          )

    # Получаем ID бренда ZTE
    brand_name = 'ZTE'  # Укажи здесь нужное название бренда вручную
    conn = op.get_bind()
    brand_id = conn.execute(
        sa.select(device_brands.c.id).where(device_brands.c.name == brand_name)
    ).scalar()

    if not brand_id:
        raise Exception(f"Бренд '{brand_name}' не найден в таблице device_brands")

    # Список моделей ZTE для добавления
    device_models = [
        {"name": "Blade A31", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Blade A6", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Blade L8", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Blade A71", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Blade A7", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Blade 20 Smart", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Blade A5", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Blade A7 (2020)", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Blade V2020", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Axon 30", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Blade X3", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Blade A5 2020", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Blade V10 Vita", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Blade V10", "type": "smartphone", "device_brand_id": brand_id},
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
    # Удаляем все добавленные модели для ZTE
    op.execute("DELETE FROM device_models WHERE device_brand_id = (SELECT id FROM device_brands WHERE name = 'ZTE')")
