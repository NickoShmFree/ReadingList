from datetime import datetime
from typing import ClassVar

from pydantic import BaseModel, Field, field_validator, ConfigDict, model_validator

from db.models.items import (
    StatusItemEnum,
    KindItemEnum,
    PriorityItemEnum,
)


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
    FORBIDDEN_TAG_CHARS: ClassVar[set[str]] = {"<", ">", "&", '"', "'", "\\", "/", ";"}

    model_config = ConfigDict(
        str_strip_whitespace=True,
        use_enum_values=True,
        frozen=True,  # Делаем иммутабельным для безопасности
    )

    title: str = Field(
        min_length=TITLE_MIN_LENGTH,
        max_length=TITLE_MAX_LENGTH,
        description="Название книги или статьи",
        examples=["Чистый код", "Грокаем алгоритмы"],
    )

    kind: KindItemEnum = Field(
        description="Тип элемента: книга или статья",
        examples=[KindItemEnum.BOOK],
    )

    status: StatusItemEnum = Field(
        description="Статус чтения: планирую, читаю, прочитал",
        examples=[StatusItemEnum.PLANNED],
        default=StatusItemEnum.PLANNED,
    )

    priority: PriorityItemEnum = Field(
        description="Приоритет чтения: низкий, средний, высокий",
        examples=[PriorityItemEnum.NORMAL],
        default=PriorityItemEnum.NORMAL,
    )

    notes: str = Field(
        description="Дополнительные заметки или описание",
        examples=["Обязательно к прочтению каждому разработчику"],
        default="",
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

        # Можно добавить дополнительные проверки
        # if title.startswith("http://") or title.startswith("https://"):
        #     raise ValueError("Название не должно быть URL")

        return title

    @field_validator("notes")
    @classmethod
    def validate_notes(cls, notes: str) -> str:
        """
        Валидация заметок.
        """
        # Проверяем минимальную длину для непустых заметок
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

    @model_validator(mode="after")
    def validate_cross_field_rules(self) -> "ItemBaseSchema":
        """
        Кросс-полевая валидация.

        Проверяет зависимости между полями.
        """
        # Пример: если статус "прочитал", заметки не могут быть пустыми
        if self.status == StatusItemEnum.DONE and not self.notes.strip():
            raise ValueError("Для прочитанных элементов необходимо добавить заметки")

        # Пример: статьи не могут иметь высокий приоритет
        if self.kind == KindItemEnum.ARTICLE and self.priority == PriorityItemEnum.HIGH:
            raise ValueError("Статьи не могут иметь высокий приоритет")

        return self


class ItemCreateSchema(ItemBaseSchema):
    """
    Схема для создания нового списка чтения.
    Наследует всю валидацию из базовой схемы.
    """

    pass


class ItemUpdateSchema(BaseModel):
    """
    Схема для обновления списка чтения.
    Все поля опциональны.
    """

    model_config = ConfigDict(
        str_strip_whitespace=True,
    )

    title: str | None = Field(
        default=None,
        min_length=ItemBaseSchema.TITLE_MIN_LENGTH,
        max_length=ItemBaseSchema.TITLE_MAX_LENGTH,
        description="Новое название",
    )

    kind: KindItemEnum | None = Field(
        default=None,
        description="Новый тип",
    )

    status: StatusItemEnum | None = Field(
        default=None,
        description="Новый статус",
    )

    priority: PriorityItemEnum | None = Field(
        default=None,
        description="Новый приоритет",
    )

    notes: str | None = Field(
        default=None,
        min_length=ItemBaseSchema.NOTES_MIN_LENGTH,
        max_length=ItemBaseSchema.NOTES_MAX_LENGTH,
        description="Новые заметки",
    )

    tags: list[str] | None = Field(
        default=None,
        description="Новый список тегов",
    )

    @model_validator(mode="after")
    def validate_at_least_one_field(self) -> "ItemUpdateSchema":
        """
        Проверяет, что передан хотя бы один параметр для обновления.
        """
        if all(value is None for value in self.model_dump().values()):
            raise ValueError("Должен быть указан хотя бы один параметр для обновления")
        return self


class ItemResponseSchema(BaseModel):
    """Схема для ответа API при чтении списка чтения."""

    model_config = ConfigDict(
        from_attributes=True,
        frozen=True,
    )

    id: int = Field(
        description="Уникальный идентификатор",
        examples=[1, 42, 100],
    )

    title: str = Field(
        description="Название",
        examples=["Чистый код"],
    )

    kind: KindItemEnum = Field(
        description="Тип элемента",
        examples=[KindItemEnum.BOOK],
    )

    status: StatusItemEnum = Field(
        description="Статус чтения",
        examples=[StatusItemEnum.PLANNED],
    )

    priority: PriorityItemEnum = Field(
        description="Приоритет",
        examples=[PriorityItemEnum.NORMAL],
    )

    notes: str = Field(
        description="Заметки",
        examples=["Обязательно к прочтению"],
    )

    tags: list[str] = Field(
        description="Теги",
        examples=[["программирование", "python"]],
        default_factory=list,
    )

    created_at: datetime = Field(
        description="Дата создания",
        examples=["2024-01-15T10:30:00Z"],
    )

    updated_at: datetime = Field(
        description="Дата последнего обновления",
        examples=["2024-01-16T14:20:00Z"],
    )
