"""Add Samsung Galaxy models

Revision ID: 5884235a8886
Revises: db5b32f25312
Create Date: 2025-02-24 14:56:42.622121

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import table, column

# revision identifiers, used by Alembic.
revision: str = '5884235a8886'
down_revision: Union[str, None] = 'db5b32f25312'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    device_brands = table('device_brands',
                          column('id', sa.Integer),
                          column('name', sa.String)
                          )

    # Получаем ID бренда Samsung
    brand_name = 'Samsung'  # Укажи здесь нужное название бренда вручную
    conn = op.get_bind()
    brand_id = conn.execute(
        sa.select(device_brands.c.id).where(device_brands.c.name == brand_name)
    ).scalar()

    if not brand_id:
        raise Exception(f"Бренд '{brand_name}' не найден в таблице device_brands")

    # Список моделей Samsung для добавления
    device_models = [
        {"name": "Galaxy A3 (2017)", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Galaxy S21 Plus", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Galaxy A5 (2015)", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Galaxy S22 Ultra", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Galaxy S21 Ultra", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Galaxy A02", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Galaxy Note 20 Ultra", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Galaxy A30s", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Galaxy Note 10", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Galaxy A23", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Galaxy S20 FE", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Galaxy A32 5G", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Galaxy A54", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Galaxy S8 Plus", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Galaxy A15", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Galaxy A13", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "S21 FE", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Galaxy A12 (2021)", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Galaxy S23 Ultra", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Galaxy J5 (2016)", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Galaxy S10", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Galaxy Note 9", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Galaxy S21", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Galaxy A51", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Galaxy A40", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Galaxy J8", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Galaxy S10 Plus", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Galaxy M12", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Galaxy A32", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Galaxy A50", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Galaxy A41", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Galaxy J4 (2018)", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Galaxy J3 (2017)", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Galaxy J5 (2017)", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Galaxy M21", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Galaxy J7 (2016)", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Galaxy S20 Plus", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Galaxy S22", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Galaxy S20 Ultra", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Galaxy S7 Edge", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Galaxy S9 Plus", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Galaxy Z Fold 4", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Galaxy S6 Edge Plus", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Galaxy A3 (2016)", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Galaxy S8", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Galaxy S9", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Galaxy J3 (2016)", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Galaxy J5 (2015)", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Galaxy J7 (2017)", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Galaxy Note 20", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Galaxy A31", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Galaxy S10e", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Galaxy A73", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Galaxy A20", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Galaxy A21s", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Galaxy Z Flip", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Galaxy A52", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Galaxy A72", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Galaxy A22", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Galaxy S20", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Galaxy A33", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Galaxy A53", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Galaxy A30", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Galaxy A70", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Galaxy M31", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Galaxy J6", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Galaxy M31s", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Galaxy S23", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Galaxy A71", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Galaxy Note 10 Plus", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Galaxy A10", "type": "smartphone", "device_brand_id": brand_id},
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
    # Удаляем все добавленные модели для Samsung
    op.execute(
        "DELETE FROM device_models WHERE device_brand_id = (SELECT id FROM device_brands WHERE name = 'Samsung')")
