from typing import TYPE_CHECKING, Sequence

from sqlalchemy.ext.asyncio.session import AsyncSession

from db.repo.app import ItemTagRepo
from db.models import ItemTagDB

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from db.models import TagDB


class ItemTagServiceDB:
    """Сервис для работы со связями между Item и Tag (M2M)."""

    def __init__(self, session: "AsyncSession") -> None:
        self.repo = ItemTagRepo(session)

    async def add(
        self,
        item_id: int,
        tags: Sequence["TagDB"],
    ) -> list[ItemTagDB]:
        models = [
            ItemTagDB(
                item_id=item_id,
                tag_id=tag.id,
            )
            for tag in tags
        ]
        await self.repo.add(models=models)
        return models

    async def delete(self, item_id: int, tags_id: list[int]):
        models_db: Sequence[ItemTagDB] = await self.repo.get_many(
            where=[ItemTagDB.item_id == item_id, ItemTagDB.tag_id.in_(tags_id)]
        )
        await self.repo.delete(models=list(models_db))
