from enum import Enum as PyEnum


from sqlalchemy import String, ForeignKey, Enum, Boolean, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, CreatedAtMixin, IdIntMixin, UpdatedAtMixin


class KindReadingListEnum(str, PyEnum):
    BOOK = "книга"
    ARTICLE = "статья"


class StatusReadingListEnum(str, PyEnum):
    PLANNED = "планирую прочитать"
    READING = "читаю"
    DONE = "прочитал"


class PriorityReadingListEnum(str, PyEnum):
    LOW = "низкий"
    NORMAL = "средний"
    HIGH = "высокий"


class ReadingListDB(Base, CreatedAtMixin, IdIntMixin, UpdatedAtMixin):
    __tablename__ = "reading_list"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    title: Mapped[str] = mapped_column(String(100), index=True)
    kind: Mapped[KindReadingListEnum] = mapped_column(
        Enum(
            KindReadingListEnum,
            name="kind_enum",
            native_enum=True,
            create_constraint=True,
        ),
    )
    status: Mapped[StatusReadingListEnum] = mapped_column(
        Enum(
            StatusReadingListEnum,
            name="status_enum",
            native_enum=True,
            create_constraint=True,
        ),
    )
    priority: Mapped[PriorityReadingListEnum] = mapped_column(
        Enum(
            PriorityReadingListEnum,
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


class ReadingListTagDB(Base, IdIntMixin):
    __tablename__ = "reading_list_tags"
    reading_list_id: Mapped[int] = mapped_column(
        ForeignKey("reading_list.id", ondelete="CASCADE"), nullable=False, index=True
    )
    tag_id: Mapped[int] = mapped_column(
        ForeignKey("tags.id", ondelete="CASCADE"), nullable=False, index=True
    )
