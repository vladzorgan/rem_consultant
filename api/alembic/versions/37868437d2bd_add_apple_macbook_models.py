"""Add Apple macbook models

Revision ID: 37868437d2bd
Revises: 5253f2171f04
Create Date: 2025-02-24 15:38:44.755587

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import column, table

# revision identifiers, used by Alembic.
revision: str = '37868437d2bd'
down_revision: Union[str, None] = '5253f2171f04'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Определяем таблицу device_brands для поиска бренда
    device_brands = table('device_brands',
                          column('id', sa.Integer),
                          column('name', sa.String)
                          )

    # Получаем ID бренда Apple
    brand_name = 'Apple'  # Укажи здесь нужное название бренда вручную
    conn = op.get_bind()
    brand_id = conn.execute(
        sa.select(device_brands.c.id).where(device_brands.c.name == brand_name)
    ).scalar()

    if not brand_id:
        raise Exception(f"Бренд '{brand_name}' не найден в таблице device_brands")

    # Список моделей MacBook для добавления
    device_models = [
        {"name": "MacBook Retina 12\" A1534 2015-2017", "type": "laptop", "device_brand_id": brand_id},
        {"name": "MacBook Air 13\" A1237, A1304 2008-2009", "type": "laptop", "device_brand_id": brand_id},
        {"name": "MacBook Air 13\" A1369 2010-2012", "type": "laptop", "device_brand_id": brand_id},
        {"name": "MacBook Air 11\" A1370 2010-2012", "type": "laptop", "device_brand_id": brand_id},
        {"name": "MacBook Air 13\" A1466 2012-2013", "type": "laptop", "device_brand_id": brand_id},
        {"name": "MacBook Air 13\" 2022", "type": "laptop", "device_brand_id": brand_id},
        {"name": "MacBook Air 13\" A2179", "type": "laptop", "device_brand_id": brand_id},
        {"name": "MacBook Air 13\" A1466 2013-2015", "type": "laptop", "device_brand_id": brand_id},
        {"name": "MacBook Air 11\" A1465 2012-2013", "type": "laptop", "device_brand_id": brand_id},
        {"name": "MacBook Air 11\" A1465 2013-2015", "type": "laptop", "device_brand_id": brand_id},
        {"name": "MacBook Air 13\" A2337 2020", "type": "laptop", "device_brand_id": brand_id},
        {"name": "MacBook Air 13\" A1466 2017", "type": "laptop", "device_brand_id": brand_id},
        {"name": "MacBook Air 13\" A1932 2018-2019", "type": "laptop", "device_brand_id": brand_id},
        {"name": "MacBook Pro 17\" A1297 2009-2012", "type": "laptop", "device_brand_id": brand_id},
        {"name": "MacBook Pro 16\" 2023", "type": "laptop", "device_brand_id": brand_id},
        {"name": "MacBook Pro 14\" 2023", "type": "laptop", "device_brand_id": brand_id},
        {"name": "MacBook Pro 13\" 2022", "type": "laptop", "device_brand_id": brand_id},
        {"name": "MacBook Pro 14\" 2021", "type": "laptop", "device_brand_id": brand_id},
        {"name": "MacBook Pro 16\" 2021", "type": "laptop", "device_brand_id": brand_id},
        {"name": "MacBook Pro 13\" A2338 2020", "type": "laptop", "device_brand_id": brand_id},
        {"name": "MacBook Pro 13\" A2289 2020", "type": "laptop", "device_brand_id": brand_id},
        {"name": "MacBook Pro 13\" A2251 2020", "type": "laptop", "device_brand_id": brand_id},
        {"name": "MacBook Pro 13\" A2159 2019", "type": "laptop", "device_brand_id": brand_id},
        {"name": "MacBook Pro 13\" A1989 2019-н.в.", "type": "laptop", "device_brand_id": brand_id},
        {"name": "MacBook Pro 16\" A2141", "type": "laptop", "device_brand_id": brand_id},
        {"name": "MacBook Pro 15\" A1990 2018-н.в.", "type": "laptop", "device_brand_id": brand_id},
        {"name": "MacBook Pro 13\" A1708 2016-2018", "type": "laptop", "device_brand_id": brand_id},
        {"name": "MacBook Pro 13\" A1706 2016-2018", "type": "laptop", "device_brand_id": brand_id},
        {"name": "MacBook Pro 15\" A1707 2016-2018", "type": "laptop", "device_brand_id": brand_id},
        {"name": "MacBook Pro 13\" A1502 2013-2015", "type": "laptop", "device_brand_id": brand_id},
        {"name": "MacBook Pro 13\" A1425 2012-2013", "type": "laptop", "device_brand_id": brand_id},
        {"name": "MacBook Pro 13\" A1278 2008-2012", "type": "laptop", "device_brand_id": brand_id},
        {"name": "MacBook Pro 15\" A1398 2013-2015", "type": "laptop", "device_brand_id": brand_id},
        {"name": "MacBook Pro 15\" A1398 2012-2013", "type": "laptop", "device_brand_id": brand_id},
        {"name": "MacBook Pro 15\" A1286 2008-2012", "type": "laptop", "device_brand_id": brand_id},
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
    # Удаляем все добавленные модели для Apple
    op.execute("DELETE FROM device_models WHERE device_brand_id = (SELECT id FROM device_brands WHERE name = 'Apple' AND type = 'laptop')")
