from abc import abstractmethod
from typing import Any, Generic, TypeVar

ModelType = TypeVar(name="ModelType", bound=Any)


class Repository(Generic[ModelType]):

    @abstractmethod
    async def add(self, **options) -> None:
        pass

    @abstractmethod
    async def get(self, **options) -> ModelType | None:
        pass

    @abstractmethod
    async def get_many(self, **options) -> list[ModelType]:
        pass

    @abstractmethod
    async def update(self, **options) -> ModelType:
        pass

    @abstractmethod
    async def delete(self, **options) -> None:
        pass

    @abstractmethod
    async def count(self, **options) -> int:
        pass

    @abstractmethod
    async def max(self, **options) -> int:
        pass
