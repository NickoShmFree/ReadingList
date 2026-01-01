"""empty message

Revision ID: e0c62369b82d
Revises: 0847583a3c8f
Create Date: 2026-01-01 22:47:08.786054

"""

from typing import Sequence, Union
from datetime import datetime
from sqlalchemy import Table, MetaData

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "e0c62369b82d"
down_revision: Union[str, Sequence[str], None] = "0847583a3c8f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # Получаем таблицы для вставки данных
    metadata = MetaData()
    metadata.reflect(bind=op.get_bind())

    users_table = metadata.tables["users"]
    items_table = metadata.tables["items"]
    tags_table = metadata.tables["tags"]
    item_tags_table = metadata.tables["item_tags"]

    # Вставляем тестовых пользователей
    op.bulk_insert(
        users_table,
        [
            {
                "id": 1,
                "display_name": "Иван Тестовый",
                "email": "ivan@example.com",
                "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # password: "secret"
                "created_at": datetime.now(),
            },
            {
                "id": 2,
                "display_name": "Анна Тестова",
                "email": "anna@example.com",
                "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # password: "secret"
                "created_at": datetime.now(),
            },
        ],
    )

    # Вставляем теги
    op.bulk_insert(
        tags_table,
        [
            # Теги для пользователя 1
            {"id": 1, "name": "программирование", "user_id": 1},
            {"id": 2, "name": "python", "user_id": 1},
            {"id": 3, "name": "алгоритмы", "user_id": 1},
            {"id": 4, "name": "базы данных", "user_id": 1},
            {"id": 5, "name": "веб-разработка", "user_id": 1},
            # Теги для пользователя 2
            {"id": 6, "name": "дизайн", "user_id": 2},
            {"id": 7, "name": "ux/ui", "user_id": 2},
            {"id": 8, "name": "фигма", "user_id": 2},
            {"id": 9, "name": "типографика", "user_id": 2},
        ],
    )

    # Вставляем элементы (items) для пользователя 1
    op.bulk_insert(
        items_table,
        [
            # Книги с высоким приоритетом
            {
                "id": 1,
                "user_id": 1,
                "title": "Чистый код",
                "kind": "BOOK",  
                "status": "PLANNED", 
                "priority": "HIGH", 
                "notes": "Обязательно к прочтению каждому разработчику",
                "is_deleted": False,
                "created_at": datetime(2024, 1, 15, 10, 30, 0),
                "updated_at": datetime(2024, 1, 15, 10, 30, 0),
            },
            {
                "id": 2,
                "user_id": 1,
                "title": "Грокаем алгоритмы",
                "kind": "BOOK",
                "status": "READING",
                "priority": "HIGH",
                "notes": "Отличная книга для понимания алгоритмов",
                "is_deleted": False,
                "created_at": datetime(2024, 1, 10, 14, 20, 0),
                "updated_at": datetime(2024, 1, 20, 16, 45, 0),
            },
            {
                "id": 3,
                "user_id": 1,
                "title": "Рефакторинг",
                "kind": "BOOK",
                "status": "DONE",
                "priority": "NORMAL",
                "notes": "Полезные паттерны рефакторинга",
                "is_deleted": False,
                "created_at": datetime(2023, 12, 5, 9, 15, 0),
                "updated_at": datetime(2024, 1, 5, 11, 30, 0),
            },
            # Статьи
            {
                "id": 4,
                "user_id": 1,
                "title": "Асинхронное программирование в Python",
                "kind": "ARTICLE",
                "status": "READING",
                "priority": "NORMAL",
                "notes": "Изучаю async/await",
                "is_deleted": False,
                "created_at": datetime(2024, 1, 25, 13, 40, 0),
                "updated_at": datetime(2024, 1, 25, 13, 40, 0),
            },
            {
                "id": 5,
                "user_id": 1,
                "title": "Оптимизация SQL запросов",
                "kind": "ARTICLE",
                "status": "DONE",
                "priority": "LOW",
                "notes": "Практические советы по работе с БД",
                "is_deleted": False,
                "created_at": datetime(2023, 11, 20, 16, 10, 0),
                "updated_at": datetime(2023, 12, 10, 12, 25, 0),
            },
            # Удаленный элемент
            {
                "id": 6,
                "user_id": 1,
                "title": "Устаревшая статья про Django 2",
                "kind": "ARTICLE",
                "status": "DONE",
                "priority": "LOW",
                "notes": "Материал устарел, нужно удалить",
                "is_deleted": False,
                "created_at": datetime(2022, 5, 10, 8, 30, 0),
                "updated_at": datetime(2023, 10, 15, 14, 50, 0),
            },
            # Элементы для пользователя 2
            {
                "id": 7,
                "user_id": 2,
                "title": "Дизайн для разработчиков",
                "kind": "BOOK",
                "status": "PLANNED",
                "priority": "HIGH",
                "notes": "Поможет понять основы дизайна",
                "is_deleted": False,
                "created_at": datetime(2024, 2, 1, 11, 20, 0),
                "updated_at": datetime(2024, 2, 1, 11, 20, 0),
            },
            {
                "id": 8,
                "user_id": 2,
                "title": "Figma для начинающих",
                "kind": "ARTICLE",
                "status": "READING",
                "priority": "NORMAL",
                "notes": "Пошаговое руководство",
                "is_deleted": False,
                "created_at": datetime(2024, 1, 28, 15, 45, 0),
                "updated_at": datetime(2024, 2, 5, 9, 30, 0),
            },
        ],
    )

    # Создаем связи между элементами и тегами
    op.bulk_insert(
        item_tags_table,
        [
            # Элемент 1 (Чистый код) - теги 1, 2
            {"item_id": 1, "tag_id": 1},  # программирование
            {"item_id": 1, "tag_id": 2},  # python
            # Элемент 2 (Грокаем алгоритмы) - теги 1, 2, 3
            {"item_id": 2, "tag_id": 1},  # программирование
            {"item_id": 2, "tag_id": 2},  # python
            {"item_id": 2, "tag_id": 3},  # алгоритмы
            # Элемент 3 (Рефакторинг) - теги 1, 2
            {"item_id": 3, "tag_id": 1},  # программирование
            {"item_id": 3, "tag_id": 2},  # python
            # Элемент 4 (Асинхронное программирование) - теги 1, 2, 5
            {"item_id": 4, "tag_id": 1},  # программирование
            {"item_id": 4, "tag_id": 2},  # python
            {"item_id": 4, "tag_id": 5},  # веб-разработка
            # Элемент 5 (Оптимизация SQL) - теги 1, 4
            {"item_id": 5, "tag_id": 1},  # программирование
            {"item_id": 5, "tag_id": 4},  # базы данных
            # Элемент 6 (Устаревшая статья) - теги 1, 2
            {"item_id": 6, "tag_id": 1},  # программирование
            {"item_id": 6, "tag_id": 2},  # python
            # Элемент 7 (Дизайн для разработчиков) - теги 6, 7
            {"item_id": 7, "tag_id": 6},  # дизайн
            {"item_id": 7, "tag_id": 7},  # ux/ui
            # Элемент 8 (Figma для начинающих) - теги 6, 7, 8, 9
            {"item_id": 8, "tag_id": 6},  # дизайн
            {"item_id": 8, "tag_id": 7},  # ux/ui
            {"item_id": 8, "tag_id": 8},  # фигма
            {"item_id": 8, "tag_id": 9},  # типографика
        ],
    )


def downgrade() -> None:
    """Downgrade schema."""

    # Удаляем все тестовые данные в обратном порядке
    op.execute("DELETE FROM item_tags")
    op.execute("DELETE FROM items")
    op.execute("DELETE FROM tags")
    op.execute("DELETE FROM users")

    # Сбрасываем sequences (для PostgreSQL)
    conn = op.get_bind()
    if conn.engine.name == "postgresql":
        op.execute("SELECT setval('users_id_seq', 1, false)")
        op.execute("SELECT setval('items_id_seq', 1, false)")
        op.execute("SELECT setval('tags_id_seq', 1, false)")
