from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, CreatedAtMixin, IdIntMixin

if TYPE_CHECKING:
    from db.models import ItemDB, TagDB


class UserDB(Base, CreatedAtMixin, IdIntMixin):
    __tablename__ = "users"

    display_name: Mapped[str] = mapped_column(String(50), index=True)
    email: Mapped[str] = mapped_column(String(length=320), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(length=1024))

    items: Mapped[list["ItemDB"]] = relationship(
        back_populates="user",
    )

    tags: Mapped[list["TagDB"]] = relationship(back_populates="user")
