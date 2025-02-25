"""add_device_brands_and_links

Revision ID: 6a059148fa84
Revises: 17da931f1ffa
Create Date: 2025-02-24 13:46:34.706300

"""
from datetime import datetime
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6a059148fa84'
down_revision: Union[str, None] = '17da931f1ffa'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Добавление брендов в device_brands
    brands = [
        {"name": "Apple"},
        {"name": "Samsung"},
        {"name": "Honor"},
        {"name": "Xiaomi"},
        {"name": "Huawei"},
        {"name": "Meizu"},
        {"name": "ASUS"},
        {"name": "Blackview"},
        {"name": "Digma"},
        {"name": "Highscreen"},
        {"name": "HTC"},
        {"name": "Lenovo"},
        {"name": "Motorola"},
        {"name": "Nokia"},
        {"name": "OnePlus"},
        {"name": "OPPO"},
        {"name": "Philips"},
        {"name": "Prestigio"},
        {"name": "Realme"},
        {"name": "Sony"},
        {"name": "ZTE"},
    ]

    op.bulk_insert(
        sa.table(
            'device_brands',
            sa.column('name', sa.String),
            sa.column('created_at', sa.DateTime),
            sa.column('updated_at', sa.DateTime),
        ),
        [
            {
                "name": brand["name"],
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            } for brand in brands
        ]
    )

def downgrade():
    # Удаление всех брендов (если нужно)
    op.execute("DELETE FROM device_brands")
