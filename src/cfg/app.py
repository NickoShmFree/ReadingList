from pathlib import Path

from pydantic import BaseModel, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from .auth import CookiesConf, AuthJWT

BASE_DIR = Path(__file__).resolve().parent


class RunCfg(BaseSettings):
    host: str = Field(default="localhost", alias="HOST")
    port: int = Field(default=8000, alias="PORT")
    allow_origins: list[str] | str = Field(
        default=["http://127.0.0.1:3000", "http://localhost:3000"],
        alias="ALLOW_ORIGINS",
    )
    reload: bool = True
    docs_url: str | None = None
    redoc_url: str | None = None
    openapi_url: str | None = None

    @field_validator("allow_origins", mode="before")
    @classmethod
    def split_origins(cls, value):
        if isinstance(value, str):
            return [v.strip() for v in value.split(",")]
        return value

    model_config = SettingsConfigDict(
        env_file=BASE_DIR.parent / "secrets" / "run_cfg.env"
    )


class AppCfg(BaseModel):
    RUN: RunCfg = RunCfg()
    COOKIES_CONF: CookiesConf = CookiesConf()
    JWT: AuthJWT = AuthJWT()


app_cfg = AppCfg()
