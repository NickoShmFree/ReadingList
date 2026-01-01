from typing import TYPE_CHECKING, Optional, Sequence

from schemas import ItemResponseSchema
from utils.exceptions import AppErrors

if TYPE_CHECKING:
    from db.provider import Provider
    from schemas import ItemCreateSchema, ItemFilters, ItemUpdateSchema
    from db.models import ItemDB, TagDB


class ItemService:
    """Сервис для управления списками чтения (Item)"""

    provider_db: "Provider"

    def __init__(self, provider_db: "Provider") -> None:
        self.provider_db = provider_db

    async def create_item(
        self, user_id: int, item_add: "ItemCreateSchema"
    ) -> ItemResponseSchema:
        """
        Создает новый элемент списка чтения (книгу или статью).

        Args:
            user_id: ID пользователя-владельца
            item_data: Данные для создания элемента

        Returns:
            Созданный элемент с тегами

        Raises:
            AppErrors.bad_request: При ошибках валидации данных
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
        Получает элемент списка чтения по ID.

        Args:
            item_id: ID элемента

        Returns:
            Элемент с тегами

        Raises:
            AppErrors.not_found: Если элемент не найден
            AppErrors.gone: Если элемент удален
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
        Получает элементы списка чтения с фильтрацией.

        Args:
            filters: Параметры фильтрации, сортировки и пагинации

        Returns:
            Список элементов, удовлетворяющих фильтрам

        Note:
            По умолчанию не включает удаленные элементы
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
            title_search=filters.title_search,
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

    async def soft_delete_item(
        self, *, item_id: int, user_id: int
    ) -> ItemResponseSchema:
        """
        Выполняет мягкое удаление элемента (помечает как удаленный).

        Args:
            item_id: ID элемента для удаления
            user_id: ID пользователя (для проверки прав)

        Returns:
            Информация об удаленном элементе

        Raises:
            AppErrors.not_found: Если элемент не найден
            AppErrors.forbidden: Если элемент принадлежит другому пользователю
            AppErrors.gone: Если элемент уже удален
        """
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
        user_id: int,
        new_item: "ItemUpdateSchema",
    ) -> ItemResponseSchema:
        """
        Обновляет элемент списка чтения.

        Args:
            user_id: ID пользователя (для проверки прав)
            update_data: Данные для обновления (должен содержать id элемента)

        Returns:
            Обновленный элемент с тегами

        Raises:
            AppErrors.not_found: Если элемент не найден
            AppErrors.forbidden: Если элемент принадлежит другому пользователю
            AppErrors.gone: Если элемент удален
        """
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

    # ==================== ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ ====================

    async def __add_tags(self, user_id: int, tags: list[str]) -> list["TagDB"]:
        """
        Находит или создает теги для пользователя.

        Args:
            user_id: ID пользователя-владельца тегов
            tag_names: Список названий тегов

        Returns:
            Список объектов TagDB (существующие и созданные)
        """
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
        """
        Создает словарь с данными для обновления элемента.

        Args:
            item: Существующий элемент из БД
            new_item: Новые данные для обновления

        Returns:
            Словарь с измененными полями
        """
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
        Сравнивает старые и новые теги, возвращая разницу.

        Args:
            tags_old: Существующие теги элемента
            tags_new: Новые теги (может быть None)

        Returns:
            Кортеж: (tag_ids_to_delete, tag_names_to_add)

        Note:
            Если tags_new = None, теги не изменяются
        """
        # Извлекаем названия старых тегов
        old_names = [tag.name for tag in tags_old]

        # Теги для удаления (по ID)
        tags_to_delete = [tag.id for tag in tags_old if tag.name not in tags_new]

        # Теги для добавления (по названию)
        tags_to_add = [name for name in tags_new if name not in old_names]

        return tags_to_delete, tags_to_add
