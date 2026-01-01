from typing import TYPE_CHECKING, Optional

from fastapi import Response

from utils.exceptions import AppErrors
from .cookie import cookie_transport
from .token import create_access_token, create_refresh_token
from .password import validate_password, hash_password


if TYPE_CHECKING:
    from schemas import UserCreateSchema, UserLoginSchema
    from .cookie import CookieTransport
    from db.models import UserDB
    from db.provider import Provider


class AuthService:
    """
    Сервис аутентификации и авторизации пользователей.

    Обеспечивает:
    1. Регистрацию новых пользователей
    2. Авторизацию существующих пользователей
    3. Выход из системы
    4. Валидацию данных при регистрации
    """

    provider_db: "Provider"
    cookie_transport: "CookieTransport"

    def __init__(self, provider_db: "Provider") -> None:

        self.provider_db = provider_db
        self.cookie_transport = cookie_transport

    async def register(self, user_data: "UserCreateSchema") -> "UserDB":
        """
        Регистрация нового пользователя.

        Выполняет:
        1. Проверку уникальности email
        2. Хэширование пароля
        3. Сохранение пользователя в БД

        Args:
            user_data: Данные пользователя для регистрации.

        Returns:
            UserDB: Созданный пользователь.

        Raises:
            AppErrors.bad_request: Если пользователь с таким email уже существует.
        """
        await self.__check_email(user_data.email)
        hashed_password = hash_password(user_data.password)
        user: "UserDB" = await self.provider_db.user.add(user_data, hashed_password)
        await self.provider_db.session.commit()
        return user

    async def login(self, credentials: "UserLoginSchema") -> Response:
        """
        Авторизация пользователя.

        Выполняет:
        1. Поиск пользователя по email
        2. Валидацию пароля
        3. Генерацию access и refresh токенов
        4. Установку токенов в cookies

        Args:
            credentials: Данные для входа (email и пароль).

        Returns:
            Response: HTTP-ответ с установленными cookies авторизации.

        Raises:
            AppErrors.unauthorized: Если email или пароль неверны.
        """
        user: Optional["UserDB"] = await self.provider_db.user.get_by_email(
            email=credentials.email
        )

        # Проверяем существование пользователя и валидность пароля
        if (
            user is None
            or validate_password(credentials.password, user.hashed_password.encode())
            is False
        ):
            raise AppErrors.unauthorized("Неверные данные (проверьте логин и пароль)")

        # Генерируем токены
        access_token = create_access_token(user)
        refresh_token = create_refresh_token(user_id=user.id)

        # Создаем ответ с cookies
        return self.cookie_transport.get_login_response(
            access_token=access_token, refresh_token=refresh_token
        )

    async def logout(self) -> Response:
        """
        Выход пользователя из системы.

        Удаляет токены авторизации из cookies пользователя.

        Returns:
            Response: HTTP-ответ с очищенными cookies авторизации.
        """
        return self.cookie_transport.get_logout_response()

    async def __check_email(self, email: str) -> None:
        """
        Проверка email на уникальность в базе данных.

        Args:
            email: Email для проверки.

        Raises:
            AppErrors.bad_request: Если пользователь с таким email уже зарегистрирован.
        """
        if await self.provider_db.user.get_by_email(email) is not None:
            raise AppErrors.bad_request(
                "Пользователь с такой почтой уже зарегистрирован."
            )
