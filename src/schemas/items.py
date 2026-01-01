from datetime import datetime, date
from typing import ClassVar

from pydantic import BaseModel, Field, field_validator, ConfigDict, model_validator

from db.models.items import (
    ItemStatusEnum,
    ItemKindEnum,
    ItemPriorityEnum,
)

from db.services_db import SortOrder, SortBy


class ItemBaseSchema(BaseModel):
    """
    Базовая схема для списков чтения.
    Содержит общие поля и валидацию.
    """

    # Константы для валидации
    TITLE_MIN_LENGTH: ClassVar[int] = 2
    TITLE_MAX_LENGTH: ClassVar[int] = 100

    NOTES_MIN_LENGTH: ClassVar[int] = 2
    NOTES_MAX_LENGTH: ClassVar[int] = 2500

    TAG_MIN_LENGTH: ClassVar[int] = 2
    TAG_MAX_LENGTH: ClassVar[int] = 50
    MAX_TAGS_COUNT: ClassVar[int] = 20

    # Запрещенные символы в тегах
    FORBIDDEN_TAG_CHARS: ClassVar[set[str]] = {"<", ">", "&", '"', "'", "\\", ";"}

    model_config = ConfigDict(
        str_strip_whitespace=True,
        use_enum_values=True,
    )

    title: str = Field(
        min_length=TITLE_MIN_LENGTH,
        max_length=TITLE_MAX_LENGTH,
        description="Название книги или статьи",
        examples=["Чистый код", "Грокаем алгоритмы"],
    )

    kind: ItemKindEnum = Field(
        description="Тип элемента: книга или статья",
        examples=[ItemKindEnum.BOOK],
    )

    status: ItemStatusEnum = Field(
        description="Статус чтения: планирую, читаю, прочитал",
        examples=[ItemStatusEnum.PLANNED],
        default=ItemStatusEnum.PLANNED,
    )

    priority: ItemPriorityEnum = Field(
        description="Приоритет чтения: низкий, средний, высокий",
        examples=[ItemPriorityEnum.NORMAL],
        default=ItemPriorityEnum.NORMAL,
    )

    notes: str | None = Field(
        description="Дополнительные заметки или описание",
        examples=["Обязательно к прочтению каждому разработчику"],
        default=None,
    )

    tags: list[str] = Field(
        default_factory=list,
        description="Список тегов для категоризации элемента",
        examples=[["программирование", "алгоритмы", "python"]],
    )

    @field_validator("title")
    @classmethod
    def validate_title(cls, title: str) -> str:
        """
        Валидация названия.

        Проверяет:
        - Двойные пробелы
        - Начинается/заканчивается пробелом (уже обработано ConfigDict)
        """
        if "  " in title:
            raise ValueError("Название не должно содержать двойных пробелов")

        return title

    @field_validator("notes")
    @classmethod
    def validate_notes(cls, notes: str | None) -> str | None:
        """
        Валидация заметок.
        """
        # Проверяем минимальную длину для непустых заметок
        if notes is not None:
            stripped = notes.strip()
            if stripped and len(stripped) < cls.NOTES_MIN_LENGTH:
                raise ValueError(
                    f"Заметки должны содержать минимум {cls.NOTES_MIN_LENGTH} символа "
                    f"или быть пустыми"
                )

            # Проверяем максимальную длину (уже есть в Field)
            if len(notes) > cls.NOTES_MAX_LENGTH:
                raise ValueError(
                    f"Заметки не должны превышать {cls.NOTES_MAX_LENGTH} символов"
                )

        return notes

    @field_validator("tags", mode="before")
    @classmethod
    def validate_and_normalize_tags(
        cls,
        tags: list[str],
    ) -> list[str]:
        """
        Валидирует и нормализует список тегов.
        """
        if not tags:
            return []

        # Удаляем дубликаты с сохранением порядка
        unique_tags = []
        seen = set()

        for tag in tags:
            if tag not in seen:
                seen.add(tag)
                unique_tags.append(tag)

        # Проверяем количество
        if len(unique_tags) > cls.MAX_TAGS_COUNT:
            raise ValueError(
                f"Количество уникальных тегов не должно превышать {cls.MAX_TAGS_COUNT}. "
                f"Получено: {len(unique_tags)}"
            )

        # Обрабатываем каждый тег
        processed_tags = []

        for i, raw_tag in enumerate(unique_tags, 1):
            # Очищаем
            cleaned = raw_tag.strip()

            # Проверяем на пустоту
            if not cleaned:
                raise ValueError(
                    f"Тег #{i} не может быть пустым или состоять только из пробелов"
                )

            # Проверяем длину
            if len(cleaned) < cls.TAG_MIN_LENGTH:
                raise ValueError(
                    f"Тег #{i} '{cleaned}' должен содержать "
                    f"минимум {cls.TAG_MIN_LENGTH} символа"
                )

            if len(cleaned) > cls.TAG_MAX_LENGTH:
                raise ValueError(
                    f"Тег #{i} '{cleaned}' не должен превышать "
                    f"{cls.TAG_MAX_LENGTH} символов"
                )

            # Проверяем запрещенные символы (оптимизированно)
            for char in cls.FORBIDDEN_TAG_CHARS:
                if char in cleaned:
                    raise ValueError(
                        f"Тег #{i} содержит недопустимый символ: {repr(char)}"
                    )

            processed_tags.append(cleaned)

        return processed_tags


class ItemCreateSchema(ItemBaseSchema):
    """
    Схема для создания нового списка чтения.
    Наследует всю валидацию из базовой схемы.
    """

    pass


class IdSchema(BaseModel):
    id: int = Field(
        description="Уникальный идентификатор",
        examples=[1, 42, 100],
    )


class ItemUpdateSchema(ItemBaseSchema, IdSchema):
    pass


class ItemResponseSchema(IdSchema, ItemBaseSchema):
    """Схема для ответа API при чтении списка чтения."""

    model_config = ConfigDict(
        from_attributes=True,
    )

    created_at: datetime = Field(
        description="Дата создания",
        examples=["2024-01-15T10:30:00Z"],
    )

    updated_at: datetime = Field(
        description="Дата последнего обновления",
        examples=["2024-01-16T14:20:00Z"],
    )


class ItemFilters(BaseModel):
    """
    Модель фильтров для элементов списка чтения.
    """

    model_config = ConfigDict(
        extra="forbid",  # Запрещаем неизвестные поля
        json_schema_extra={
            "example": {
                "status": "планирую прочитать",
                "kind": "книга",
                "priority": "средний",
                "title_search": "чистый",
                "tag_names": ["python", "алгоритмы"],
                "created_from": "2024-01-01",
                "created_to": "2024-12-31",
                "sort_by": "created_at",
                "sort_order": "desc",
                "offset": 0,
                "limit": 20,
            }
        },
    )

    status: ItemStatusEnum | None = Field(None, description="Фильтр по статусу чтения")

    kind: ItemKindEnum | None = Field(
        None, description="Фильтр по типу элемента (книга/статья)"
    )

    priority: ItemPriorityEnum | None = Field(
        None, description="Фильтр по приоритету чтения"
    )

    title_search: str | None = Field(
        None,
        min_length=2,
        max_length=50,
        description="Поиск по подстроке в названии (регистронезависимый)",
    )
    tag_names: list[str] | None = Field(
        None,
        description="Фильтр по названиям тегов",
        max_length=20,
    )

    created_from: date | None = Field(
        None, description="Начало диапазона дат создания (включительно)"
    )

    created_to: date | None = Field(
        None, description="Конец диапазона дат создания (включительно)"
    )

    include_deleted: bool = Field(False, exclude=True)

    sort_by: SortBy = Field(
        SortBy.CREATED_AT, description="Поле для сортировки результатов"
    )

    sort_order: SortOrder = Field(SortOrder.DESC, description="Направление сортировки")

    offset: int = Field(
        0,
        ge=0,
        le=10000,
        description="Смещение для пагинации (сколько элементов пропустить)",
    )

    limit: int = Field(
        20,
        ge=1,
        le=100,
        description="Количество элементов на странице",
    )

    @field_validator("tag_names")
    @classmethod
    def validate_tags(cls, v: list[str] | None) -> list[str] | None:
        if v:
            # Очищаем и дедуплицируем теги
            cleaned = {tag.strip().lower() for tag in v if tag.strip()}
            if not cleaned:
                return None
            return list(cleaned)
        return v

    @field_validator("sort_order")
    @classmethod
    def validate_sort_order(cls, v: str) -> str:
        if v not in {"asc", "desc"}:
            raise ValueError("sort_order должно быть 'asc' или 'desc'")
        return v

    @model_validator(mode="after")
    def validate_date_range(self) -> "ItemFilters":
        """Кросс-полевая валидация: диапазон дат."""
        if self.created_from and self.created_to:
            if self.created_from > self.created_to:
                raise ValueError("Дата 'created_from' не может быть позже 'created_to'")
        today = date.today()
        if self.created_from and self.created_from > today:
            raise ValueError("Дата 'created_from' не может быть в будущем")

        if self.created_to and self.created_to > today:
            raise ValueError("Дата 'created_to' не может быть в будущем")

        return self
