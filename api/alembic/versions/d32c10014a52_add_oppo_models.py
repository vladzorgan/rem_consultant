"""Add Oppo models

Revision ID: d32c10014a52
Revises: af7cee6b62ba
Create Date: 2025-02-24 15:17:07.211094

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import column, table

# revision identifiers, used by Alembic.
revision: str = 'd32c10014a52'
down_revision: Union[str, None] = 'af7cee6b62ba'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Определяем таблицу device_brands для поиска бренда
    device_brands = table('device_brands',
                          column('id', sa.Integer),
                          column('name', sa.String)
                          )

    # Получаем ID бренда Oppo
    brand_name = 'OPPO'  # Укажи здесь нужное название бренда вручную
    conn = op.get_bind()
    brand_id = conn.execute(
        sa.select(device_brands.c.id).where(device_brands.c.name == brand_name)
    ).scalar()

    if not brand_id:
        raise Exception(f"Бренд '{brand_name}' не найден в таблице device_brands")

    # Список моделей Oppo для добавления
    device_models = [
        {"name": "Reno6", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "A55", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "A72", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "F9", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "A5s", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "R11", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "R15x", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "R17", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "A53", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Reno2", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Reno4", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Reno Z", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "6", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "F5 Youth", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Find X2", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Reno3 Pro", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "A5", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "A91", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "A74", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Find X3 Pro", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "A71", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Reno3", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "A1K", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Reno5 Lite", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "A52", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "F11", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Find X3", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Reno 10x Zoom", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "R15", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "F7 Youth", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Reno", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "A5 2020", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "R11s", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "A9 2020", "type": "smartphone", "device_brand_id": brand_id},
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
    # Удаляем все добавленные модели для Oppo
    op.execute("DELETE FROM device_models WHERE device_brand_id = (SELECT id FROM device_brands WHERE name = 'OPPO')")
