from enum import Enum as PyEnum
from typing import TYPE_CHECKING

from sqlalchemy import String, ForeignKey, Enum, Boolean, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, CreatedAtMixin, IdIntMixin, UpdatedAtMixin

if TYPE_CHECKING:
    from db.models import UserDB


class ItemKindEnum(str, PyEnum):
    BOOK = "книга"
    ARTICLE = "статья"


class ItemStatusEnum(str, PyEnum):
    PLANNED = "планирую прочитать"
    READING = "читаю"
    DONE = "прочитал"


class ItemPriorityEnum(str, PyEnum):
    LOW = "низкий"
    NORMAL = "средний"
    HIGH = "высокий"


class ItemDB(Base, CreatedAtMixin, IdIntMixin, UpdatedAtMixin):
    __tablename__ = "items"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    title: Mapped[str] = mapped_column(String(100), index=True)
    kind: Mapped[ItemKindEnum] = mapped_column(
        Enum(
            ItemKindEnum,
            name="item_kind_enum",
            native_enum=True,
            create_constraint=True,
        ),
    )
    status: Mapped[ItemStatusEnum] = mapped_column(
        Enum(
            ItemStatusEnum,
            name="item_status_enum",
            native_enum=True,
            create_constraint=True,
        ),
    )
    priority: Mapped[ItemPriorityEnum] = mapped_column(
        Enum(
            ItemPriorityEnum,
            name="item_priority_enum",
            native_enum=True,
            create_constraint=True,
        ),
    )

    notes: Mapped[str] = mapped_column(String(2500))

    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)

    user: Mapped["UserDB"] = relationship(
        back_populates="items",
    )

    item_tags: Mapped[list["ItemTagDB"]] = relationship(
        back_populates="item",
        cascade="all, delete-orphan",
    )


class TagDB(Base, IdIntMixin):
    __tablename__ = "tags"
    name: Mapped[str] = mapped_column(String(50))
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    user: Mapped["UserDB"] = relationship(back_populates="tags")

    item_tags: Mapped[list["ItemTagDB"]] = relationship(
        back_populates="tag",
        cascade="all, delete-orphan",
    )

    __table_args__ = (UniqueConstraint("user_id", "name", name="uq_user_id_name"),)


class ItemTagDB(Base, IdIntMixin):
    __tablename__ = "item_tags"
    item_id: Mapped[int] = mapped_column(
        ForeignKey("items.id", ondelete="CASCADE"), nullable=False, index=True
    )
    tag_id: Mapped[int] = mapped_column(
        ForeignKey("tags.id", ondelete="CASCADE"), nullable=False, index=True
    )

    item: Mapped["ItemDB"] = relationship(back_populates="item_tags")

    tag: Mapped["TagDB"] = relationship(
        back_populates="item_tags",
        order_by="TagDB.name.asc()",
    )
