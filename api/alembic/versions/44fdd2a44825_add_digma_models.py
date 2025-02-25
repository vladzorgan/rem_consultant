"""Add Digma models

Revision ID: 44fdd2a44825
Revises: ac7e95db4eaf
Create Date: 2025-02-24 15:05:29.922022

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import column, table

# revision identifiers, used by Alembic.
revision: str = '44fdd2a44825'
down_revision: Union[str, None] = 'ac7e95db4eaf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Определяем таблицу device_brands для поиска бренда
    device_brands = table('device_brands',
                          column('id', sa.Integer),
                          column('name', sa.String)
                          )

    # Получаем ID бренда Digma
    brand_name = 'Digma'  # Укажи здесь нужное название бренда вручную
    conn = op.get_bind()
    brand_id = conn.execute(
        sa.select(device_brands.c.id).where(device_brands.c.name == brand_name)
    ).scalar()

    if not brand_id:
        raise Exception(f"Бренд '{brand_name}' не найден в таблице device_brands")

    # Список моделей Digma для добавления
    device_models = [
        {"name": "VOX V40 3G", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Linx B510 3G", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Linx Alfa 3G", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Linx Pay 4G", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Linx Argo 3G", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Linx Atom 3G", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Linx A453 3G", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "Vox S507 4G", "type": "smartphone", "device_brand_id": brand_id},
        {"name": "HIT Q500 3G", "type": "smartphone", "device_brand_id": brand_id},
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
    # Удаляем все добавленные модели для Digma
    op.execute("DELETE FROM device_models WHERE device_brand_id = (SELECT id FROM device_brands WHERE name = 'Digma')")
