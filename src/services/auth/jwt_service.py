import uuid
from datetime import UTC, datetime, timedelta

import jwt
from fastapi.encoders import jsonable_encoder

from cfg.app import app_cfg


def encode_jwt(
    payload: dict,
    private_key: str,
    algorithm: str,
    expire_minutes: int,
    expire_timedelta: timedelta | None = None,
) -> str:
    to_encode = jsonable_encoder(payload)
    now: datetime = datetime.now(UTC)
    if expire_timedelta:
        expire = now + expire_timedelta
    else:
        expire = now + timedelta(minutes=expire_minutes)
    to_encode.update(
        exp=expire,
        iat=now,
        jti=str(uuid.uuid4()),
    )
    encoded = jwt.encode(
        to_encode,
        private_key,
        algorithm=algorithm,
    )
    return encoded


def decode_jwt(
    token: str,
    public_key: str = app_cfg.JWT.public_key_path.read_text(),
    algorithm: str = app_cfg.JWT.algorithm,
):
    decode = jwt.decode(token, public_key, algorithms=[algorithm])
    return decode
