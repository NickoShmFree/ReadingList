from typing import TYPE_CHECKING, Sequence

from sqlalchemy.ext.asyncio.session import AsyncSession

from db.repo.app import TagRepo
from db.models import TagDB

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class TagServiceDB:
    """Сервис для работы с таблицей tags (теги)"""

    def __init__(self, session: "AsyncSession") -> None:
        self.repo = TagRepo(session)

    async def add(
        self,
        user_id: int,
        tags: list[str],
    ) -> list[TagDB]:
        """
        Добавляет теги для пользователя.

        Args:
            user_id: ID пользователя
            tags: Список названий тегов для добавления

        Returns:
            Список новых тегов пользователя
        """
        models = [TagDB(user_id=user_id, name=tag) for tag in tags]
        await self.repo.add(models=models)
        return models

    async def get_existing_and_new_tags(
        self,
        user_id: int,
        tags: list[str],
    ) -> tuple[Sequence[TagDB], list[str]]:
        """
        Разделяет теги на существующие и новые.

        Returns:
            Кортеж (существующие_теги, новые_названия)
        """
        existing_tags = await self.repo.get_many(
            where=[TagDB.user_id == user_id, TagDB.name.in_(tags)]
        )
        existing_names = {tag.name for tag in existing_tags}
        new_tag_names = [name for name in tags if name not in existing_names]

        return existing_tags, new_tag_names
