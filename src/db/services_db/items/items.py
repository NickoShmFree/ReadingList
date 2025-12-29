from typing import TYPE_CHECKING

from sqlalchemy.ext.asyncio.session import AsyncSession

from db.repo.app import ItemRepo
from db.models import ItemDB

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from schemas import ItemCreateSchema


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
