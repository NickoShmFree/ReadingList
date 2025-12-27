from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

BASE_DIR = Path(__file__).resolve().parent


class DBCfg(BaseSettings):

    host: str = Field(default="localhost", alias="HOST")
    port: int = Field(default=5432, alias="PORT")
    user: str = Field(default="postgres", alias="POSTGRES_USER")
    password: str = Field(default="password", alias="POSTGRES_PASSWORD")
    name_db: str | None = Field(default=None, alias="NAME_DB")

    pool_size: int = 50
    max_overflow: int = 50
    pool_timeout: int = 60
    schemas: str = "postgresql+asyncpg"
    expire_on_commit: bool = False

    @property
    def conn_string(self) -> str:
        return f"{self.schemas}://{self.user}:{self.password}@{self.host}:{self.port}/{self.name_db}"

    model_config = SettingsConfigDict(env_file=BASE_DIR.parent / "secrets" / "db.env")


db_cfg = DBCfg()
