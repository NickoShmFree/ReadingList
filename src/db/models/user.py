from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, CreatedAtMixin, IdIntMixin


class UserDB(Base, CreatedAtMixin, IdIntMixin):
    __tablename__ = "users"

    display_name: Mapped[str] = mapped_column(String(50), index=True)
    email: Mapped[str] = mapped_column(String(length=320), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(length=1024))
