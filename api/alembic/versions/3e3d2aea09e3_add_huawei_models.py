"""Add Huawei models

Revision ID: 3e3d2aea09e3
Revises: aeb23774e456
Create Date: 2025-02-24 15:01:00.090800

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import column, table

# revision identifiers, used by Alembic.
revision: str = '3e3d2aea09e3'
down_revision: Union[str, None] = 'aeb23774e456'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    device_brands = table('device_brands',
                          column('id', sa.Integer),
                          column('name', sa.String)
                          )

    # Получаем ID бренда Huawei
    brand_name = 'Huawei'  # Укажи здесь нужное название бренда вручную
    conn = op.get_bind()
    brand_id = conn.execute(
        sa.select(device_brands.c.id).where(device_brands.c.name == brand_name)
    ).scalar()

    if not brand_id:
        raise Exception(f"Бренд '{brand_name}' не найден в таблице device_brands")

    # Список моделей Huawei для добавления
    device_models = [
        {"name": "Nova y90", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Mate 20 Lite", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Mate 20 Pro", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "P Smart", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Mate X3", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Mate 20", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "P30", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "P Smart 2019", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "P40", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Ascend P7", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Y9S", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Nova 10 Pro", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "P20 Pro", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "P9 Pro", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Nova 5T", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "P40 Lite E", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Nova 8i", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Nova 9", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "P50 Pro", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "P30 lite New Edition", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Y5p", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "P20 Lite", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Nova 3", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Y6s", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "P30 Pro", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Mate Xs", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Nova", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "P Smart Z", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Y8p", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "P smart 2021", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Y5 (2019)", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Y6p", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "P40 Pro", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Nova 2", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "P30 Lite", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Y6 (2019)", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Mate 40 Pro", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Nova 8", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "P40 Pro+", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Y7 (2019)", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Mate 30 Pro", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "P20", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Nova 2s", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Mate 20 X", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "P40 Lite", "type": "smartphone", "device_brand_id": brand_id},
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
    # Удаляем все добавленные модели для Huawei
    op.execute("DELETE FROM device_models WHERE device_brand_id = (SELECT id FROM device_brands WHERE name = 'Huawei')")
