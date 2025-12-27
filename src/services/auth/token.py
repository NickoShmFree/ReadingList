from typing import TYPE_CHECKING
from datetime import timedelta

from .jwt_service import encode_jwt
from cfg.app import app_cfg
from schemas import JWTPayloadAccess, JWTPayloadRefresh
from cfg.auth import TokenType

if TYPE_CHECKING:
    from db.models import UserDB


def create_jwt(
    token_type: str,
    token_data: dict,
    private_key: str = app_cfg.JWT.private_key_path.read_text(),
    algorithm: str = app_cfg.JWT.algorithm,
    expire_minutes: int = app_cfg.JWT.access_token_expire_minutes,
    expire_timedelta: timedelta | None = None,
) -> str:
    """Создание JWT токена.

    Args:
        token_type (str): Тип токена (access или refresh).
        token_data (dict): Данные, которые будут включены в токен.
        private_key (str): Приватный ключ для подписи токена.
        algorithm (str): Алгоритм подписи.
        expire_minutes (int): Время действия токена в минутах.
        expire_timedelta (timedelta, optional): Параметры для времени действия токена.

    Returns:
        str: Подписанный JWT токен.
    """
    jwt_payload = {app_cfg.JWT.TOKEN_TYPE_FIELD: token_type}
    jwt_payload.update(token_data)
    return encode_jwt(
        payload=jwt_payload,
        private_key=private_key,
        algorithm=algorithm,
        expire_minutes=expire_minutes,
        expire_timedelta=expire_timedelta,
    )


def create_access_token(user: "UserDB") -> str:
    """Создание access токена.

    Args:
        role: "UserRole"
        user_id (int): Id пользователя, для которого создается токен.
        tsn_id: (int): Id ТСН, в который заходит пользователь

    Returns:
        str: Access токен.
    """
    jwt_payload = JWTPayloadAccess(
        sub=str(user.id),
        display_name=user.display_name,
    ).model_dump(serialize_as_any=True)
    return create_jwt(
        token_type=TokenType.access,
        token_data=jwt_payload,
    )


def create_refresh_token(user_id: int) -> str:
    """Создание refresh токена.

    Args:
        user_id (int): Id пользователя, для которого создается токен.
        tsn_id: (int): Id ТСН, в который заходит пользователь

    Returns:
        str: Refresh токен.
    """
    jwt_payload = JWTPayloadRefresh(sub=str(user_id)).model_dump(serialize_as_any=True)
    return create_jwt(
        token_type=TokenType.refresh,
        token_data=jwt_payload,
        expire_timedelta=timedelta(days=app_cfg.JWT.refresh_token_expire_days),
    )
