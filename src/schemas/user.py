import re
from datetime import datetime
from typing import ClassVar, Final

from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict


class PasswordConfig:
    """
    Конфигурация строгих требований к паролям.

    Требует:
    - Длина: 8-64 символа
    - Строчные и заглавные латинские буквы
    - Цифры
    - Специальные символы
    """

    MIN_LENGTH: Final[int] = 8
    MAX_LENGTH: Final[int] = 64

    # Паттерны для проверки сложности
    PATTERNS: ClassVar[dict[str, re.Pattern]] = {
        "lowercase": re.compile(r"[a-z]"),  # строчные латинские
        "uppercase": re.compile(r"[A-Z]"),  # заглавные латинские
        "digit": re.compile(r"\d"),  # цифры
        "special": re.compile(r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?]'),  # спецсимволы
    }

    ERROR_MESSAGES: ClassVar[dict[str, str]] = {
        "min_length": f"Пароль должен содержать минимум {MIN_LENGTH} символов",
        "max_length": f"Пароль не должен превышать {MAX_LENGTH} символов",
        "lowercase": "Пароль должен содержать хотя бы одну строчную латинскую букву (a-z)",
        "uppercase": "Пароль должен содержать хотя бы одну заглавную латинскую букву (A-Z)",
        "digit": "Пароль должен содержать хотя бы одну цифру (0-9)",
        "special": "Пароль должен содержать хотя бы один специальный символ (!@#$%^&*()_+-=[]{};':\"\\|,.<>/?)",
        "sequential": "Пароль не должен состоять из последовательных символов (123456, abcdef)",
        "repetitive": "Пароль не должен состоять из повторяющихся символов (aaaaaa, 111111)",
    }

    @classmethod
    def get_requirements_text(cls) -> str:
        """Текст требований для отображения пользователю."""
        return (
            f"Пароль должен быть от {cls.MIN_LENGTH} до {cls.MAX_LENGTH} символов и содержать:\n"
            "- Строчные латинские буквы (a-z)\n"
            "- Заглавные латинские буквы (A-Z)\n"
            "- Цифры (0-9)\n"
            "- Специальные символы (!@#$%^&*()_+-=[]{};':\"\\|,.<>/?)"
        )


class PasswordSchema(BaseModel):
    """
    Схема для валидации паролей со строгими требованиями.

    Требования:
    - Длина от 8 до 64 символов
    - Не должен быть в списке распространенных паролей
    - Должен содержать: латинские буквы (строчные и заглавные), цифры, специальные символы
    - Не должен состоять из последовательностей или повторений
    """

    model_config = ConfigDict(
        str_strip_whitespace=True,
        str_min_length=PasswordConfig.MIN_LENGTH,
        str_max_length=PasswordConfig.MAX_LENGTH,
    )

    password: str = Field(
        description="Пароль пользователя",
        examples=["StrongPass123!", "MyP@ssw0rd2024"],
        min_length=PasswordConfig.MIN_LENGTH,
        max_length=PasswordConfig.MAX_LENGTH,
    )

    @field_validator("password")
    @classmethod
    def validate_password(cls, password: str) -> str:
        """
        Строгая валидация пароля.

        Args:
            password: Введенный пароль

        Returns:
            Валидированный пароль

        Raises:
            ValueError: Если пароль не соответствует требованиям
        """
        # Проверка на повторения
        if cls._is_too_repetitive(password):
            raise ValueError(PasswordConfig.ERROR_MESSAGES["repetitive"])

        # Проверка сложности
        checks = [
            ("lowercase", PasswordConfig.PATTERNS["lowercase"]),
            ("uppercase", PasswordConfig.PATTERNS["uppercase"]),
            ("digit", PasswordConfig.PATTERNS["digit"]),
            ("special", PasswordConfig.PATTERNS["special"]),
        ]

        for check_name, pattern in checks:
            if not pattern.search(password):
                raise ValueError(PasswordConfig.ERROR_MESSAGES[check_name])

        return password

    @staticmethod
    def _is_too_repetitive(password: str) -> bool:
        """Проверяет, состоит ли пароль из повторяющихся символов."""
        if len(password) < 3:
            return False

        # Все символы одинаковые
        if len(set(password)) == 1:
            return True

        # Проверка повторяющихся пар (aabbcc, 112233)
        for i in range(len(password) - 2):
            if password[i] == password[i + 1] == password[i + 2]:
                return True

        return False


class UserBaseSchema(BaseModel):
    """
    Базовая схема с общими полями пользователя.
    """

    DISPLAY_NAME_MIN_LENGTH: ClassVar[int] = 2
    DISPLAY_NAME_MAX_LENGTH: ClassVar[int] = 50
    EMAIL_MAX_LENGTH: ClassVar[int] = 255

    model_config = ConfigDict(
        str_strip_whitespace=True,
        str_min_length=DISPLAY_NAME_MIN_LENGTH,
        frozen=True,
        extra="forbid",
    )

    email: EmailStr = Field(
        description="Электронная почта пользователя",
        examples=["user@example.com", "ivan.ivanov@gmail.com"],
        json_schema_extra={"format": "email"},
        max_length=EMAIL_MAX_LENGTH,
    )

    display_name: str = Field(
        description="Отображаемое имя пользователя",
        examples=["Иван Иванов", "Alex", "Кодер2000"],
        min_length=DISPLAY_NAME_MIN_LENGTH,
        max_length=DISPLAY_NAME_MAX_LENGTH,
    )

    @field_validator("email")
    @classmethod
    def validate_email(cls, email: str) -> str:
        """Расширенная валидация email."""
        # Приводим к нижнему регистру
        normalized = email.lower().strip()

        # Проверяем длину после нормализации
        if len(normalized) > cls.EMAIL_MAX_LENGTH:
            raise ValueError(
                f"Email не должен превышать {cls.EMAIL_MAX_LENGTH} символов"
            )
        return normalized

    @field_validator("display_name")
    @classmethod
    def validate_display_name(cls, name: str) -> str:
        """
        Валидация отображаемого имени.

        Проверяет:
        1. Недопустимые символы
        2. Формат (не email, не только цифры)
        3. Двойные пробелы
        """
        if "@" in name:
            raise ValueError("Имя пользователя не может содержать символ @")

        if name.isdigit():
            raise ValueError("Имя пользователя не может состоять только из цифр")
        forbidden_pattern = re.compile(r'[<>"&\\/;]')
        if forbidden_pattern.search(name):
            raise ValueError(
                "Имя содержит недопустимые символы. "
                "Разрешены: буквы, цифры, пробелы, дефисы (-), апострофы ('), точки (.)"
            )
        if "  " in name:
            raise ValueError("Имя не должно содержать двойных пробелов")

        return name


class UserCreateSchema(UserBaseSchema, PasswordSchema):
    """
    Схема для создания нового пользователя (регистрация).

    Объединяет базовые данные пользователя и пароль.
    """

    pass


class UserReadSchema(BaseModel):
    """
    Схема для ответа API при чтении пользователя.

    Содержит все публичные данные пользователя.
    Используется в эндпоинтах типа GET /users/{id}
    """

    model_config = ConfigDict(
        from_attributes=True,  # Для создания из ORM моделей
        frozen=True,
    )

    id: int = Field(
        description="Уникальный идентификатор пользователя",
        examples=[1, 42, 100],
    )

    email: EmailStr = Field(
        description="Электронная почта пользователя",
        examples=["user@example.com"],
    )

    display_name: str = Field(
        description="Отображаемое имя пользователя",
        examples=["Иван Иванов"],
    )


class CurrentUserSchema(UserReadSchema):
    """Схема для данных текущего аутентифицированного пользователя."""

    pass
