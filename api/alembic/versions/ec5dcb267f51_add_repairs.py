"""Add repairs

Revision ID: ec5dcb267f51
Revises: a806ff1c033d
Create Date: 2025-02-24 17:25:26.198424

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import table, column

# revision identifiers, used by Alembic.
revision: str = 'ec5dcb267f51'
down_revision: Union[str, None] = 'a806ff1c033d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    repairs = [
        {"name": "Диагностика"},
        {"name": "Замена вибромотора"},
        {"name": "Замена аккумулятора"},
        {"name": "Замена разъема зарядки "},
        {"name": "Замена контроллера питания"},
        {"name": "Замена корпуса"},
        {"name": "Замена задней крышки"},
        {"name": "Замена разъема наушников "},
        {"name": "Замена динамика"},
        {"name": "Замена динамиков"},
        {"name": "Замена аудиокодека"},
        {"name": "Замена основной камеры"},
        {"name": "Замена передней камеры"},
        {"name": "Замена кнопки Home (домой)"},
        {"name": "Замена кнопки включения"},
        {"name": "Замена кнопок громкости"},
        {"name": "Замена кнопки переключения вибро"},
        {"name": "Снятие пароля"},
        {"name": "Обновление ПО"},
        {"name": "Программный ремонт"},
        {"name": "Ремонт Wi-Fi модуля"},
        {"name": "Восстановление после попадания влаги"},
        {"name": "Замена микрофона"},
        {"name": "Замена SIM-держателя (механизм)"},
        {"name": "Замена антенны"},
        {"name": "Замена стекла"},
        {"name": "Замена экрана"},
        {"name": "Замена датчика приближения"},
    ]

    # Вставляем модели в таблицу device_models
    op.bulk_insert(
        table('repairs',
              column('name', sa.String),
              column('created_at', sa.DateTime),
              column('updated_at', sa.DateTime)
              ),
        repairs
    )


def downgrade() -> None:
    op.execute("DELETE * FROM repairs")