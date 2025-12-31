from typing import (
    TypeVar,
    Generic,
    Sequence,
    Any,
    overload,
    TYPE_CHECKING,
    Literal,
    Union,
    Tuple,
)

from sqlalchemy import select, func, UnaryExpression, ColumnElement

from db import models
from .base import Repository

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy.orm import InstrumentedAttribute
    from sqlalchemy.orm.interfaces import ORMOption


Model = TypeVar("Model", bound=models.Base)
IdLike = Any | tuple[Any, ...]
T = TypeVar("T")


class SARepository(Repository, Generic[Model]):

    def __init__(self, session: "AsyncSession", model_type: type[Model]):
        """Инициализация репозитория с сессией и моделью."""
        self.session = session
        self.model_type = model_type

    @overload
    async def add(self, *, model: Model, commit: bool = False) -> None:
        pass

    @overload
    async def add(self, *, models: list[Model], commit: bool = False) -> None:
        pass

    async def add(
        self,
        *,
        model: Model | None = None,
        models: list[Model] | None = None,
        commit: bool = False,
    ) -> None:
        """Создать новую запись в базе."""
        if model is not None:
            self.session.add(model)
            await self.session.flush()
        elif models is not None:
            self.session.add_all(models)
        else:
            raise ValueError("Необходимо передать либо model, либо models.")
        if commit:
            await self.session.commit()
            if model:
                await self.session.refresh(model)

    @overload
    async def get(
        self,
        *,
        ident: IdLike | None,
        options: Sequence["ORMOption"] | None = None,
        joins: Sequence["InstrumentedAttribute"] | None = None,
    ) -> Model | None:
        pass

    @overload
    async def get(
        self,
        *,
        where: Sequence[ColumnElement[bool]] | None,
        options: Sequence["ORMOption"] | None = None,
        joins: Sequence["InstrumentedAttribute"] | None = None,
    ) -> Model | None:
        pass

    async def get(
        self,
        *,
        ident: IdLike | None = None,
        where: Sequence[ColumnElement[bool]] | None = None,
        options: Sequence["ORMOption"] | None = None,
        joins: Sequence["InstrumentedAttribute"] | None = None,
    ) -> Model | None:
        """Получить объект из базы. Если не найден — вернуть None."""
        if ident is not None:
            return await self.session.get(self.model_type, ident, options=options)
        if where:
            stmt = select(self.model_type).where(*where)
            if joins:
                for table in joins:
                    stmt = stmt.join(table)
            if options:
                stmt = stmt.options(*options)
            cursor = await self.session.execute(stmt)
            return cursor.scalar_one_or_none()
        raise ValueError("Either 'ident' or 'where' must be provided")

    async def get_many(
        self,
        *,
        where: Sequence[ColumnElement[bool]] = (),
        limit: int = 10,
        offset: int = 0,
        order_by: Sequence[UnaryExpression] = (),
        options: Sequence["ORMOption"] | None = None,
        joins: (
            Sequence[
                Union[
                    "InstrumentedAttribute",
                    Tuple["InstrumentedAttribute", ColumnElement[bool] | None],
                ]
            ]
            | None
        ) = None,
        join_type: Literal["inner", "left"] = "inner",
        select_from: Any | None = None,
        distinct: bool = False,
    ) -> Sequence[Model]:
        """Получить список записей из базы с расширенной поддержкой JOIN."""
        stmt = select(self.model_type if select_from is None else select_from)

        if distinct:
            stmt = stmt.distinct()

        # Обработка JOIN
        if joins:
            join_func = stmt.join if join_type == "inner" else stmt.outerjoin

            for join_item in joins:
                # Проверяем тип join_item
                if isinstance(join_item, tuple) and len(join_item) == 2:
                    table, on_clause = join_item
                    if on_clause is not None:  # Явная проверка на None
                        stmt = join_func(table, onclause=on_clause)
                    else:
                        stmt = join_func(table)
                else:
                    # Простой JOIN без условия ON
                    stmt = join_func(join_item)

        stmt = stmt.where(*where).order_by(*order_by).limit(limit).offset(offset)

        if options:
            stmt = stmt.options(*options)

        res = await self.session.execute(stmt)
        return res.scalars().all()

    @overload
    async def update(
        self, *, db_model: Model, data_update: dict, commit: bool = False
    ) -> Model:
        pass

    @overload
    async def update(
        self, *, ident: IdLike, data_update: dict, commit: bool = False
    ) -> Model:
        pass

    async def update(
        self,
        *,
        ident: IdLike | None = None,
        db_model: Model | None = None,
        data_update: dict,
        commit: bool = False,
    ) -> Model:
        """Обновить объект в базе."""
        if (
            db_model is not None
            and ident is not None
            or db_model is None
            and ident is None
        ):
            raise ValueError("bad arguments")
        if db_model is None:
            db_model = await self.get(ident=ident)
        if not db_model:
            raise ValueError(f"{self.model_type.__name__} с ID {ident} не найден")

        for field, value in data_update.items():
            setattr(db_model, field, value)

        if commit:
            await self.session.commit()
            await self.session.refresh(db_model)

        return db_model

    async def delete(
        self,
        *,
        model: Model | None = None,
        models: list[Model] | None = None,
        commit: bool = False,
    ) -> None:
        """Удалить объект или несколько объектов из базы."""
        if (model is None and models is None) or (
            model is not None and models is not None
        ):
            raise ValueError(
                "You must provide either 'model' or 'models', but not both or neither."
            )
        if models is not None:
            for row in models:
                await self.session.delete(row)

        if model is not None:
            await self.session.delete(model)

        if commit:
            await self.session.commit()

    async def count(
        self,
        where: Sequence[ColumnElement[bool]] = (),
        joins: Sequence | None = None,
    ) -> int:
        """Подсчитать количество записей в базе с возможными JOIN-ами."""
        stmt = select(func.count()).select_from(self.model_type)

        if joins:
            for join_model in joins:
                stmt = stmt.join(join_model)

        stmt = stmt.where(*where)

        res = await self.session.execute(stmt)
        return res.scalar_one_or_none() or 0

    async def max(self, attr: ColumnElement[T]) -> T | None:
        """Получить максимальное значение атрибута."""
        stmt = select(func.max(attr))
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()  # Возвращаем None, если данных нет
