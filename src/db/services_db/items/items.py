from datetime import date, datetime
from typing import TYPE_CHECKING, Sequence
from enum import Enum

from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select

from db.repo.app import ItemRepo
from db.models import ItemDB, ItemTagDB, TagDB

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from schemas import ItemCreateSchema


class SortBy(str, Enum):
    CREATED_AT = "created_at"
    UPDATED_AT = "updated_at"
    PRIORITY = "priority"


class SortOrder(str, Enum):
    ASC = "asc"
    DESC = "desc"


class ItemServiceDB:
    """Сервис для работы с таблицей users (пользователи)"""

    def __init__(self, session: "AsyncSession") -> None:
        self.repo = ItemRepo(session)

    async def add(
        self,
        user_id: int,
        item: "ItemCreateSchema",
    ) -> ItemDB:
        model = ItemDB(
            user_id=user_id,
            title=item.title,
            kind=item.kind,
            status=item.status,
            priority=item.priority,
            notes=item.notes,
        )
        await self.repo.add(model=model)
        return model

    async def get_by_id(
        self, item_id: int, *, load_tags: bool = False
    ) -> ItemDB | None:
        options = []
        if load_tags is True:
            options.append(selectinload(ItemDB.item_tags).joinedload(ItemTagDB.tag))
        return await self.repo.get(ident=item_id, options=options)

    async def get_items(
        self,
        *,
        load_tags: bool = False,
        offset: int = 0,
        limit: int = 20,
        created_from: date | None = None,
        created_to: date | None = None,
        title_search: str | None = None,
        tag_names: list[str] | None = None,
        sort_by: SortBy = SortBy.CREATED_AT,
        sort_order: SortOrder = SortOrder.DESC,
        **filters,
    ) -> Sequence[ItemDB]:

        options = []
        if load_tags:
            options.append(selectinload(ItemDB.item_tags).joinedload(ItemTagDB.tag))

        where_conditions = [ItemDB.is_deleted == False]
        ALLOWED_FIELDS = {"user_id", "status", "kind", "priority"}

        for field, value in filters.items():
            if field in ALLOWED_FIELDS and hasattr(ItemDB, field):
                column = getattr(ItemDB, field)
                if value is not None:
                    where_conditions.append(column == value)

        if title_search and title_search.strip():
            search_term = f"%{title_search.strip()}%"
            where_conditions.append(ItemDB.title.ilike(search_term))

        if created_from:
            from_dt = datetime.combine(created_from, datetime.min.time())
            where_conditions.append(ItemDB.created_at >= from_dt)

        if created_to:
            to_dt = datetime.combine(created_to, datetime.max.time())
            where_conditions.append(ItemDB.created_at <= to_dt)

        # Фильтрация по тегам через подзапрос
        if tag_names:
            # Создаем подзапрос для элементов с нужными тегами
            tag_subquery = (
                select(ItemTagDB.item_id)
                .join(TagDB, ItemTagDB.tag_id == TagDB.id)
                .where(TagDB.name.in_(tag_names))
                .distinct()
            )

            # Добавляем условие
            where_conditions.append(ItemDB.id.in_(tag_subquery))

        sort_map = {
            SortBy.CREATED_AT: [ItemDB.created_at],
            SortBy.UPDATED_AT: [ItemDB.updated_at],
            SortBy.PRIORITY: [ItemDB.priority],
        }

        columns = sort_map[sort_by]
        order_columns = [
            col.asc() if sort_order == SortOrder.ASC else col.desc() for col in columns
        ]

        return await self.repo.get_many(
            where=where_conditions,
            options=options,
            offset=offset,
            limit=limit,
            order_by=order_columns,
        )

    async def update(self, item: ItemDB, **data_update):
        await self.repo.update(db_model=item, data_update=data_update)
