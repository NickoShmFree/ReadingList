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
