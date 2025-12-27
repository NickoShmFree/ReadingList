from typing import Literal, Optional, cast

from fastapi import Request, Response, status

from cfg.app import app_cfg


class CookieTransport:
    def __init__(
        self,
        *,
        cookie_name_access_token: str = app_cfg.COOKIES_CONF.access_token,
        cookie_name_refresh_token: str = app_cfg.COOKIES_CONF.refresh_token,
        cookie_max_age: int | None = app_cfg.COOKIES_CONF.max_age,
        cookie_secure: bool = app_cfg.COOKIES_CONF.secure,
        cookie_httponly: bool = app_cfg.COOKIES_CONF.httponly,
        cookie_samesite_access_token: Literal["lax", "strict", "none"] = cast(
            Literal["lax", "strict", "none"], app_cfg.COOKIES_CONF.samesite_access_token
        ),
        cookie_samesite_refresh_token: Literal["lax", "strict", "none"] = cast(
            Literal["lax", "strict", "none"],
            app_cfg.COOKIES_CONF.samesite_refresh_token,
        ),
    ):
        self.cookie_name_access_token = cookie_name_access_token
        self.cookie_name_refresh_token = cookie_name_refresh_token
        self.cookie_max_age = cookie_max_age
        self.cookie_secure = cookie_secure
        self.cookie_httponly = cookie_httponly

        # Явно приводим к нужному типу
        self.cookie_samesite_access_token: Literal["lax", "strict", "none"] = cast(
            Literal["lax", "strict", "none"], cookie_samesite_access_token
        )
        self.cookie_samesite_refresh_token: Literal["lax", "strict", "none"] = cast(
            Literal["lax", "strict", "none"], cookie_samesite_refresh_token
        )

    async def get_access_token(self, request: Request) -> Optional[str]:
        """Получить access token из куки"""
        return request.cookies.get(self.cookie_name_access_token)

    async def get_refresh_token(self, request: Request) -> Optional[str]:
        """Получить refresh token из куки"""
        return request.cookies.get(self.cookie_name_refresh_token)

    def get_login_response(self, access_token: str, refresh_token: str) -> Response:
        response = Response(status_code=status.HTTP_204_NO_CONTENT)
        return self.__set_login_cookies(
            response, access_token=access_token, refresh_token=refresh_token
        )

    def get_logout_response(self) -> Response:
        response = Response(status_code=status.HTTP_204_NO_CONTENT)
        return self.__set_logout_cookies(response)

    def __set_login_cookies(
        self, response: Response, access_token: str, refresh_token: str
    ) -> Response:
        # Access token cookie
        response.set_cookie(
            key=self.cookie_name_access_token,
            value=access_token,
            max_age=self.cookie_max_age,
            secure=self.cookie_secure,
            httponly=self.cookie_httponly,
            samesite=self.cookie_samesite_access_token,
        )

        # Refresh token cookie
        response.set_cookie(
            key=self.cookie_name_refresh_token,
            value=refresh_token,
            max_age=self.cookie_max_age,
            secure=self.cookie_secure,
            httponly=self.cookie_httponly,
            samesite=self.cookie_samesite_refresh_token,
        )

        return response

    def __set_logout_cookies(self, response: Response) -> Response:
        """Очистить куки при logout"""
        response.delete_cookie(
            self.cookie_name_access_token,
            secure=self.cookie_secure,
            httponly=self.cookie_httponly,
            samesite=self.cookie_samesite_access_token,
        )
        response.delete_cookie(
            self.cookie_name_refresh_token,
            secure=self.cookie_secure,
            httponly=self.cookie_httponly,
            samesite=self.cookie_samesite_refresh_token,
        )
        return response


cookie_transport = CookieTransport()
