from typing import TYPE_CHECKING, Annotated, Optional

from fastapi import Depends, Response

from utils.exceptions import AppErrors
from services.auth.cookie import cookie_transport
from db.connector import get_provider
from services import AuthService, ItemService
from .get_current_user import CurrentUser

if TYPE_CHECKING:
    from db.provider import Provider


def get_auth_service(
    provider: Annotated["Provider", Depends(get_provider)],
) -> AuthService:
    return AuthService(provider)


def get_reading_list_service(
    provider: Annotated["Provider", Depends(get_provider)],
) -> ItemService:
    return ItemService(provider)


def get_current_user_service(
    provider: Annotated["Provider", Depends(get_provider)],
    access_token: Annotated[Optional[str], Depends(cookie_transport.get_access_token)],
    refresh_token: Annotated[
        Optional[str], Depends(cookie_transport.get_refresh_token)
    ],
    response: Response,
) -> CurrentUser:
    if access_token is None or refresh_token is None:
        raise AppErrors.unauthorized("Требуется авторизация")

    return CurrentUser(
        provider,
        access_token=access_token,
        refresh_token=refresh_token,
        response=response,
        cookie_transport=cookie_transport,
    )
