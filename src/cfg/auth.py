from pathlib import Path
from typing import Literal
from enum import Enum

from pydantic import BaseModel


BASE_DIR = Path(__file__).resolve().parent


class TokenType(str, Enum):
    access = "access"
    refresh = "refresh"


class AuthJWT(BaseModel):
    TOKEN_TYPE_FIELD: str = "type"

    private_key_path: Path = BASE_DIR.parent / "secrets" / "certs" / "jwt-private.pem"
    public_key_path: Path = BASE_DIR.parent / "secrets" / "certs" / "jwt-public.pem"
    algorithm: str = "RS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7


class CookiesConf(BaseModel):
    access_token: str = "access_token"
    refresh_token: str = "refresh_token"
    httponly: bool = True
    max_age: int = 604800
    secure: bool = True
    samesite_access_token: Literal["lax", "strict", "none"] = "lax"
    samesite_refresh_token: Literal["lax", "strict", "none"] = "strict"
