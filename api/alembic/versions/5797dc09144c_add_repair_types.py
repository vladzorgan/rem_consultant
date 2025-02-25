"""Add repair_types

Revision ID: 5797dc09144c
Revises: b2f7a19dfc2e
Create Date: 2025-02-24 16:51:33.141496

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5797dc09144c'
down_revision: Union[str, None] = 'b2f7a19dfc2e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Добавление данных в таблицу repair_types
    op.bulk_insert(
        sa.table(
            'repair_types',
            sa.column('group_name', sa.String),
            sa.column('name', sa.String)
        ),
        [
            # Группа: Вибрация
            {'group_name': 'Вибрация', 'name': 'Не работает вибрация'},
            {'group_name': 'Вибрация', 'name': 'Громко гудит'},
            {'group_name': 'Вибрация', 'name': 'Не всегда срабатывает'},

            # Группа: Зарядка
            {'group_name': 'Зарядка', 'name': 'Греется'},
            {'group_name': 'Зарядка', 'name': 'Не заряжается'},
            {'group_name': 'Зарядка', 'name': 'Плохой контакт'},
            {'group_name': 'Зарядка', 'name': 'Быстро садится'},

            # Группа: Задняя крышка
            {'group_name': 'Задняя крышка', 'name': 'Поцарапана зад. крышка'},
            {'group_name': 'Задняя крышка', 'name': 'Треснула зад. крышка'},
            {'group_name': 'Задняя крышка', 'name': 'Разбит полностью'},

            # Группа: Динамики
            {'group_name': 'Динамики', 'name': 'Не работают наушники'},
            {'group_name': 'Динамики', 'name': 'Динамик хрипит'},
            {'group_name': 'Динамики', 'name': 'Динамик тихий'},
            {'group_name': 'Динамики', 'name': 'Динамик не работает'},

            # Группа: Камера
            {'group_name': 'Камера', 'name': 'Не работает (задняя) камера'},
            {'group_name': 'Камера', 'name': 'Не фокусирует (передняя) камера'},
            {'group_name': 'Камера', 'name': 'Не работает (передняя) камера'},

            # Группа: Кнопки
            {'group_name': 'Кнопки', 'name': 'Сломалась центральная кнопка (Home)'},
            {'group_name': 'Кнопки', 'name': 'Сломалась кнопка вкл/выкл'},
            {'group_name': 'Кнопки', 'name': 'Сломалась кнопка громкости'},
            {'group_name': 'Кнопки', 'name': 'Сломалась кнопка вибро'},

            # Группа: Общие проблемы
            {'group_name': 'Общие проблемы', 'name': 'Забыт пароль'},
            {'group_name': 'Общие проблемы', 'name': 'Не включается'},
            {'group_name': 'Общие проблемы', 'name': 'Просит Itunes'},
            {'group_name': 'Общие проблемы', 'name': 'Не работает Wi-Fi'},
            {'group_name': 'Общие проблемы', 'name': 'Попала влага'},
            {'group_name': 'Общие проблемы', 'name': 'Зависает (обновить ПО)'},

            # Группа: Разговор
            {'group_name': 'Разговор', 'name': 'Я не слышу собеседника'},
            {'group_name': 'Разговор', 'name': 'Собеседник меня не слышит'},
            {'group_name': 'Разговор', 'name': 'Я плохо слышу собеседника'},
            {'group_name': 'Разговор', 'name': 'Собеседник меня плохо слышит'},

            # Группа: Связь (Сеть)
            {'group_name': 'Связь (Сеть)', 'name': 'Не видит SIM'},
            {'group_name': 'Связь (Сеть)', 'name': 'Сеть ловит плохо'},
            {'group_name': 'Связь (Сеть)', 'name': 'Нет сети'},

            # Группа: Экран/дисплей
            {'group_name': 'Экран/дисплей', 'name': 'Не работает часть экрана'},
            {'group_name': 'Экран/дисплей', 'name': 'Разбилось или поцарапалось стекло'},
            {'group_name': 'Экран/дисплей', 'name': 'Нет подсветки'},
            {'group_name': 'Экран/дисплей', 'name': 'Не работает часть или весь сенсор'},
        ]
    )


def downgrade():
    # Удаление всех данных из таблицы repair_types
    op.execute("DELETE FROM repair_types")
