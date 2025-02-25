"""Add laptop brands and links

Revision ID: 989c0c923ba7
Revises: 6a059148fa84
Create Date: 2025-02-24 13:53:03.938602

"""
from datetime import datetime
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '989c0c923ba7'
down_revision: Union[str, None] = '6a059148fa84'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Новые бренды для добавления в device_brands
    new_brands = [
        {"name": "Acer"},
        {"name": "Dell"},
        {"name": "HP"},
        {"name": "MSI"},
        {"name": "Toshiba"},
    ]

    # Добавляем новые бренды
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
            } for brand in new_brands
        ]
    )

def downgrade():
    # Удаляем добавленные ссылки
    op.execute("DELETE FROM device_brand_links WHERE path LIKE '/remont-noutbukov/%' OR path = '/remont-apple/macbook'")
    # Удаляем новые бренды
    op.execute("DELETE FROM device_brands WHERE name IN ('MacBook', 'Acer', 'Dell', 'HP', 'MSI', 'Toshiba')")
