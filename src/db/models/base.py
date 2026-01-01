from datetime import datetime
from typing import Annotated

from sqlalchemy import TIMESTAMP
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import func

timestamp = Annotated[
    datetime,
    mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
    ),
]


class Base(DeclarativeBase):
    __abstract__ = True
    type_annotation_map = {
        datetime: TIMESTAMP(timezone=True),
    }


class IdIntMixin:
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)


class CreatedAtMixin:
    """Mixin для добавления created_at с временем создания записи"""

    created_at: Mapped[timestamp] = mapped_column(
        default=func.now(),
        server_default=func.now(),
    )


class UpdatedAtMixin:
    """Mixin для добавления updated_at с временем последнего обновления"""

    updated_at: Mapped[timestamp] = mapped_column(
        default=func.now(),
        server_default=func.now(),
        onupdate=func.now(),
    )
