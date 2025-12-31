from typing import TYPE_CHECKING, Optional, Sequence

from schemas import ItemResponseSchema, ItemResponseSchema
from utils.exceptions import AppErrors

if TYPE_CHECKING:
    from db.provider import Provider
    from schemas import ItemCreateSchema, ItemFilters, ItemUpdateSchema
    from db.models import ItemDB, TagDB, ItemTagDB


class ItemService:
    """Сервис для управления списками чтения (Item)"""

    provider_db: "Provider"

    def __init__(self, provider_db: "Provider") -> None:
        self.provider_db = provider_db

    async def add(
        self, user_id: int, item_add: "ItemCreateSchema"
    ) -> ItemResponseSchema:
        """
        Создает новую книгу (статью) чтения с тегами.

        Args:
            user_id: ID пользователя
            item_add: Данные для создания

        Returns:
            Созданный список чтения
        """
        result_tags: list["TagDB"] = []
        item: "ItemDB" = await self.provider_db.item.add(user_id, item_add)
        if item_add.tags:
            result_tags = await self.__add_tags(user_id, item_add.tags)
            await self.provider_db.item_tag.add(item.id, result_tags)
        await self.provider_db.session.commit()
        return ItemResponseSchema(
            id=item.id,
            title=item.title,
            kind=item.kind,
            status=item.status,
            priority=item.priority,
            notes=item.notes,
            tags=[row.name for row in result_tags],
            created_at=item.created_at,
            updated_at=item.updated_at,
        )

    async def get_item(self, item_id: int) -> ItemResponseSchema:
        """
        Получает элемент по ID.

        Args:
            item_id: ID элемента
        Returns:
            Элемент с тегами

        Raises:
            HTTPException 404: Если элемент не найден
        """
        item: Optional["ItemDB"] = await self.provider_db.item.get_by_id(
            item_id, load_tags=True
        )
        if item is None:
            raise AppErrors.not_found("Элемент не найден")
        if item.is_deleted is True:
            raise AppErrors.gone("Элемент удален")

        return ItemResponseSchema(
            id=item.id,
            title=item.title,
            status=item.status,
            kind=item.kind,
            priority=item.priority,
            notes=item.notes,
            tags=[item_tag.tag.name for item_tag in item.item_tags],
            created_at=item.created_at,
            updated_at=item.updated_at,
        )

    async def get_items(
        self,
        filters: "ItemFilters",
    ) -> list[ItemResponseSchema]:
        """
        Получает элемент по ID.

        Args:
            item_id: ID элемента
        Returns:
            Элемент с тегами

        Raises:
            HTTPException 404: Если элемент не найден
        """

        items: Sequence["ItemDB"] = await self.provider_db.item.get_items(
            load_tags=True,
            tag_names=filters.tag_names,
            created_to=filters.created_to,
            created_from=filters.created_from,
            sort_by=filters.sort_by,
            sort_order=filters.sort_order,
            offset=filters.offset,
            limit=filters.limit,
            status=filters.status,
            priority=filters.priority,
            kind=filters.kind,
        )
        return [
            ItemResponseSchema(
                id=item.id,
                title=item.title,
                kind=item.kind,
                status=item.status,
                priority=item.priority,
                notes=item.notes,
                tags=[item_tag.tag.name for item_tag in item.item_tags],
                created_at=item.created_at,
                updated_at=item.updated_at,
            )
            for item in items
        ]

    async def del_item(self, *, item_id: int, user_id: int) -> ItemResponseSchema:
        item: Optional["ItemDB"] = await self.provider_db.item.get_by_id(
            item_id, load_tags=True
        )
        if item is None:
            raise AppErrors.not_found("Элемент не найден")
        if item.user_id != user_id:
            raise AppErrors.forbidden("Элемент принадлежит другому пользователю")
        if item.is_deleted is True:
            raise AppErrors.gone("Элемент уже удален")
        await self.provider_db.item.update(item, is_deleted=True)
        data = ItemResponseSchema(
            id=item.id,
            title=item.title,
            kind=item.kind,
            status=item.status,
            priority=item.priority,
            notes=item.notes,
            tags=[item_tag.tag.name for item_tag in item.item_tags],
            created_at=item.created_at,
            updated_at=item.updated_at,
        )
        await self.provider_db.session.commit()
        return data

    async def update_item(
        self,
        *,
        user_id: int,
        new_item: "ItemUpdateSchema",
    ) -> ItemResponseSchema:
        item: Optional["ItemDB"] = await self.provider_db.item.get_by_id(
            new_item.id, load_tags=True
        )
        if item is None:
            raise AppErrors.not_found("Элемент не найден")
        if item.user_id != user_id:
            raise AppErrors.forbidden("Элемент принадлежит другому пользователю")
        if item.is_deleted is True:
            raise AppErrors.gone("Элемент удален")
        update_data = self.__create_update_data(item, new_item=new_item)

        tags_to_delete, tags_to_add = self.__compare_tags_simple(
            tags_new=new_item.tags,
            tags_old=[item_tag.tag for item_tag in item.item_tags],
        )
        if tags_to_delete:
            await self.provider_db.item_tag.delete(item.id, tags_to_delete)

        if tags_to_add:
            result_tags: list["TagDB"] = await self.__add_tags(user_id, tags_to_add)
            await self.provider_db.item_tag.add(item.id, result_tags)

        await self.provider_db.item.update(item, **update_data)
        await self.provider_db.session.commit()
        await self.provider_db.session.refresh(item)
        return ItemResponseSchema(
            id=item.id,
            title=item.title,
            kind=item.kind,
            status=item.status,
            priority=item.priority,
            notes=item.notes,
            tags=[item_tag.tag.name for item_tag in item.item_tags],
            created_at=item.created_at,
            updated_at=item.updated_at,
        )

    async def __add_tags(self, user_id: int, tags: list[str]) -> list["TagDB"]:
        existing_tags, new_tag_names = (
            await self.provider_db.tag.get_existing_and_new_tags(user_id, tags)
        )
        if new_tag_names:
            new_tags: Sequence["TagDB"] = await self.provider_db.tag.add(
                user_id, new_tag_names
            )
            await self.provider_db.session.flush()
            result_tags: list["TagDB"] = list(existing_tags) + list(new_tags)
        else:
            result_tags = list(existing_tags)
        return result_tags

    async def __del_item_tags(self, user_id: int, tags: list[str]) -> list["TagDB"]:
        existing_tags, new_tag_names = (
            await self.provider_db.tag.get_existing_and_new_tags(user_id, tags)
        )
        if new_tag_names:
            new_tags: Sequence["TagDB"] = await self.provider_db.tag.add(
                user_id, new_tag_names
            )
            await self.provider_db.session.flush()
            result_tags: list["TagDB"] = list(existing_tags) + list(new_tags)
        else:
            result_tags = list(existing_tags)
        return result_tags

    def __create_update_data(self, item: "ItemDB", new_item: "ItemUpdateSchema"):
        update_data = {}
        if item.title != new_item.title:
            update_data["title"] = new_item.title
        if item.kind != new_item.kind:
            update_data["kind"] = new_item.kind
        if item.status != new_item.status:
            update_data["status"] = new_item.status
        if item.priority != new_item.priority:
            update_data["priority"] = new_item.priority
        if item.notes != new_item.notes:
            update_data["notes"] = new_item.notes
        return update_data

    def __compare_tags_simple(
        self, *, tags_old: list["TagDB"], tags_new: list[str]
    ) -> tuple[list[int], list[str]]:
        """
        Простая версия сравнения тегов.
        """
        # Извлекаем названия старых тегов
        old_names = [tag.name for tag in tags_old]

        # Теги для удаления (по ID)
        tags_to_delete = [tag.id for tag in tags_old if tag.name not in tags_new]

        # Теги для добавления (по названию)
        tags_to_add = [name for name in tags_new if name not in old_names]

        return tags_to_delete, tags_to_add
