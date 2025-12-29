from typing import TYPE_CHECKING, Sequence

from schemas import ItemResponseSchema

if TYPE_CHECKING:
    from db.provider import Provider
    from schemas import ItemCreateSchema
    from db.models import ItemDB, TagDB


class ItemService:
    """Сервис для управления списками чтения (Item)"""

    provider_db: "Provider"

    def __init__(self, provider_db: "Provider") -> None:
        self.provider_db = provider_db

    async def add(self, user_id: int, item: "ItemCreateSchema") -> ItemResponseSchema:
        """
        Создает новую книгу (статью) чтения с тегами.

        Args:
            user_id: ID пользователя
            item: Данные для создания

        Returns:
            Созданный список чтения
        """
        result_tags: list["TagDB"] = []
        reading_list: "ItemDB" = await self.provider_db.reading_list.add(user_id, item)
        if item.tags:
            existing_tags, new_tag_names = (
                await self.provider_db.tag.get_existing_and_new_tags(user_id, item.tags)
            )
            if new_tag_names:
                new_tags: Sequence["TagDB"] = await self.provider_db.tag.add(
                    user_id, new_tag_names
                )
                await self.provider_db.session.flush()
                result_tags = list(existing_tags) + list(new_tags)
            else:
                result_tags = list(existing_tags)
            await self.provider_db.reading_list_tag.add(reading_list.id, result_tags)
        await self.provider_db.session.commit()
        return ItemResponseSchema(
            id=reading_list.id,
            title=reading_list.title,
            kind=reading_list.kind,
            status=reading_list.status,
            priority=reading_list.priority,
            notes=reading_list.notes,
            tags=[row.name for row in result_tags],
            created_at=reading_list.created_at,
            updated_at=reading_list.updated_at,
        )
