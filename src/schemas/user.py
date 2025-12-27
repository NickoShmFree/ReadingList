import re
from datetime import datetime
from dataclasses import dataclass

from pydantic import BaseModel, EmailStr, Field, field_validator


@dataclass
class PasswordConfig:
    MIN_LENGTH = 6
    MAX_LENGTH = 100
    PATTERNS = {
        "lowercase": re.compile(r"[a-z]"),
        "uppercase": re.compile(r"[A-Z]"),
        "digit": re.compile(r"\d"),
        "special": re.compile(r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?]'),
    }
    ERROR_MESSAGES = {
        "min_length": "Пароль должен содержать минимум 6 символов",
        "max_length": "Пароль не должен превышать 100 символов",
        "lowercase": "Пароль должен содержать хотя бы одну строчную букву",
        "uppercase": "Пароль должен содержать хотя бы одну заглавную букву",
        "digit": "Пароль должен содержать хотя бы одну цифру",
        "special": "Пароль должен содержать хотя бы один специальный символ",
    }


class PasswordSchema(BaseModel):
    password: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        # TODO после тестов поставить валидацию пароля
        # v = v.strip()

        # # Проверка длины
        # if len(v) < PasswordConfig.MIN_LENGTH:
        #     raise ValueError(PasswordConfig.ERROR_MESSAGES["min_length"])
        # if len(v) > PasswordConfig.MAX_LENGTH:
        #     raise ValueError(PasswordConfig.ERROR_MESSAGES["max_length"])

        # # Проверка сложности
        # checks = [
        #     ("lowercase", PasswordConfig.PATTERNS["lowercase"]),
        #     ("uppercase", PasswordConfig.PATTERNS["uppercase"]),
        #     ("digit", PasswordConfig.PATTERNS["digit"]),
        #     ("special", PasswordConfig.PATTERNS["special"]),
        # ]

        # for check_name, pattern in checks:
        #     if not pattern.search(v):
        #         raise ValueError(PasswordConfig.ERROR_MESSAGES[check_name])

        return v


class UserAddSchema(BaseModel):
    email: EmailStr = Field(description="email пользователя")
    display_name: str = Field(description="Имя пользователя")

    @field_validator("display_name")
    @classmethod
    def validate_name_length(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 2:
            raise ValueError("Имя должно содержать минимум 2 символа")
        if len(v) > 50:
            raise ValueError("Имя не должно превышать 50 символов")
        return v


class UserCreateSchema(UserAddSchema, PasswordSchema):
    pass


class UserReadSchema(UserAddSchema):
    id: int = Field(description="id пользователя")
    created_at: datetime = Field(description="Дата регистрации пользователя")
