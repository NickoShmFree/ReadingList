from typing import TYPE_CHECKING, Optional, overload, Literal

from fastapi import Response
from jwt import InvalidTokenError

from services.auth.jwt_service import decode_jwt
from utils.exceptions import AppErrors
from services.auth.token import create_access_token
from schemas import (
    JWTPayloadAccess,
    JWTPayloadRefresh,
    CurrentUserSchema,
)
from cfg.auth import TokenType

if TYPE_CHECKING:
    from db.provider import Provider
    from services.auth.cookie import CookieTransport
    from db.models import UserDB


class CurrentUser:
    """
    Класс для управления текущим пользователем через JWT-токены в cookies.
    """

    provider_db: "Provider"
    response: Response
    cookie_transport: "CookieTransport"
    access_token: str
    refresh_token: str

    def __init__(
        self,
        provider_db: "Provider",
        *,
        response: Response,
        cookie_transport: "CookieTransport",
        access_token: str,
        refresh_token: str,
    ) -> None:
        """
        Args:
            service_db (UserServiceDB): сервис для работы с пользователями в базе данных.
            response (Response): куки
            cookie_transport (CookieTransport): сервис для работы с куками.
            access_token (str):
            refresh_token (str):
        """
        self.provider_db = provider_db
        self.response = response
        self.cookie_transport = cookie_transport
        self.access_token = access_token
        self.refresh_token = refresh_token

    async def get_user_by_token(
        self,
    ) -> CurrentUserSchema:
        """
        Получаем пользователя по токену

        Args:
            require_chairman: Если True, требует роль председателя

        Raises:
            AppErrors.unauthorized: Invalid refresh token
            AppErrors.forbidden: Недостаточно прав

        Returns:
            CurrentUserRead: Текущий пользователь
        """
        # Пробуем декодировать access token
        payload: JWTPayloadAccess | None = self.__decode_token(
            token_type=TokenType.access, token=self.access_token
        )

        if payload:
            return CurrentUserSchema(
                id=int(payload.sub),
                email=payload.email,
                display_name=payload.display_name,
            )

        # Если access token невалиден, пробуем refresh token
        payload_refresh: JWTPayloadRefresh | None = self.__decode_token(
            token_type=TokenType.refresh, token=self.refresh_token
        )
        if not payload_refresh:
            raise AppErrors.unauthorized(detail="Invalid refresh token")

        return await self.__refresh_access_token(payload_refresh)

    async def __refresh_access_token(
        self, payload: JWTPayloadRefresh
    ) -> CurrentUserSchema:
        """
        Обновляем токен доступа

        Args:
            payload: payload из refresh токена
            require_chairman: требует ли эндпоинт роль председателя

        Returns:
            CurrentUserRead: Текущий пользователь
        """
        user: Optional["UserDB"] = await self.provider_db.user.get_by_id(
            user_id=int(payload.sub)
        )
        if not user:
            self.cookie_transport.get_logout_response()
            raise AppErrors.unauthorized("Пользователь не найден")

        self.__set_access_token_cookie(user)

        return CurrentUserSchema(
            id=int(payload.sub),
            email=user.email,
            display_name=user.display_name,
        )

    def __set_access_token_cookie(self, user: "UserDB") -> None:
        """
        Устанавливаем новый токен доступа в куки

        Args:
            user: Модель БД текущего пользователя
            tsn_resident: Модель БД жителя ТСН
        """
        new_access_token = create_access_token(user)
        self.response.set_cookie(
            key=self.cookie_transport.cookie_name_access_token,
            value=new_access_token,
            httponly=self.cookie_transport.cookie_httponly,
            max_age=self.cookie_transport.cookie_max_age,
            secure=self.cookie_transport.cookie_secure,
            samesite=self.cookie_transport.cookie_samesite_access_token,
        )

    @overload
    @staticmethod
    def __decode_token(
        *, token_type: Literal[TokenType.access], token: str
    ) -> JWTPayloadAccess | None:
        pass

    @overload
    @staticmethod
    def __decode_token(
        *, token_type: Literal[TokenType.refresh], token: str
    ) -> JWTPayloadRefresh | None:
        pass

    @staticmethod
    def __decode_token(
        *, token_type: Literal[TokenType.access, TokenType.refresh], token: str
    ) -> JWTPayloadAccess | JWTPayloadRefresh | None:
        """
        Декодируем токен и возвращаем его в виде словаря

        Args:
            token_type: тип токена (access или refresh)
            token: токен для декодирования

        Returns:
            payload из токена или None для access token при ошибке
        """
        try:
            payload = decode_jwt(token)
            if token_type == TokenType.access:
                return JWTPayloadAccess(**payload)
            return JWTPayloadRefresh(**payload)
        except InvalidTokenError:
            if token_type == TokenType.access:
                return None
            raise AppErrors.unauthorized("Invalid token")
