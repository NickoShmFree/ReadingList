from typing import TYPE_CHECKING, Annotated

from fastapi import Depends

from db.connector import get_provider
from services import AuthService

if TYPE_CHECKING:
    from db.provider import Provider


def get_auth_service(
    provider: Annotated["Provider", Depends(get_provider)],
) -> AuthService:
    return AuthService(provider)
