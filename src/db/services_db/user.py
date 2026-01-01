from typing import TYPE_CHECKING

from sqlalchemy.ext.asyncio.session import AsyncSession

from db.repo.app import UserRepo
from db.models import UserDB


if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from schemas import UserCreateSchema


class UserServiceDB:
    """Сервис для работы с таблицей users (пользователи)"""

    def __init__(self, session: "AsyncSession") -> None:
        self.repo = UserRepo(session)

    async def add(
        self,
        user: "UserCreateSchema",
        hashed_password: str,
    ) -> UserDB:
        model = UserDB(
            display_name=user.display_name,
            email=user.email,
            hashed_password=hashed_password,
        )
        await self.repo.add(model=model)
        return model

    async def get_by_email(self, email: str) -> UserDB | None:
        return await self.repo.get(where=[UserDB.email == email])

    async def get_by_id(self, user_id: int) -> UserDB | None:
        return await self.repo.get(ident=user_id)
