from enum import Enum as PyEnum


from sqlalchemy import String, ForeignKey, Enum, Boolean, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, CreatedAtMixin, IdIntMixin, UpdatedAtMixin


class KindItemEnum(str, PyEnum):
    BOOK = "книга"
    ARTICLE = "статья"


class StatusItemEnum(str, PyEnum):
    PLANNED = "планирую прочитать"
    READING = "читаю"
    DONE = "прочитал"


class PriorityItemEnum(str, PyEnum):
    LOW = "низкий"
    NORMAL = "средний"
    HIGH = "высокий"


class ItemDB(Base, CreatedAtMixin, IdIntMixin, UpdatedAtMixin):
    __tablename__ = "reading_list"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    title: Mapped[str] = mapped_column(String(100), index=True)
    kind: Mapped[KindItemEnum] = mapped_column(
        Enum(
            KindItemEnum,
            name="kind_enum",
            native_enum=True,
            create_constraint=True,
        ),
    )
    status: Mapped[StatusItemEnum] = mapped_column(
        Enum(
            StatusItemEnum,
            name="status_enum",
            native_enum=True,
            create_constraint=True,
        ),
    )
    priority: Mapped[PriorityItemEnum] = mapped_column(
        Enum(
            PriorityItemEnum,
            name="priority_enum",
            native_enum=True,
            create_constraint=True,
        ),
    )

    notes: Mapped[str] = mapped_column(String(2500))

    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)


class TagDB(Base, IdIntMixin):
    __tablename__ = "tags"
    name: Mapped[str] = mapped_column(String(50))
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    __table_args__ = (UniqueConstraint("user_id", "name", name="uq_user_id_name"),)


class ItemTagDB(Base, IdIntMixin):
    __tablename__ = "reading_list_tags"
    reading_list_id: Mapped[int] = mapped_column(
        ForeignKey("reading_list.id", ondelete="CASCADE"), nullable=False, index=True
    )
    tag_id: Mapped[int] = mapped_column(
        ForeignKey("tags.id", ondelete="CASCADE"), nullable=False, index=True
    )
