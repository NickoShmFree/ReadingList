# import logging
# from logging.config import dictConfig
from contextlib import asynccontextmanager
import uvicorn

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from cfg.app import app_cfg
from cfg.logging import LOGGING_CONFIG

# Настройка логирования
# dictConfig(LOGGING_CONFIG)
# logger = logging.getLogger("app")

# from api import router
# from db.connector import ConnectionManager


# @asynccontextmanager
# async def lifespan(app_: FastAPI):
#     manager = ConnectionManager()
#     manager.connect()
#     yield
#     await manager.disconnect()


app = FastAPI(
    # lifespan=lifespan,
    # docs_url=app_conf.run.docs_url,
    # redoc_url=app_conf.run.redoc_url,
    # openapi_url=app_conf.run.openapi_url,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=app_cfg.RUN.allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# app.include_router(router)


if __name__ == "__main__":
    # logger.info(f"Запуск сервера на http://{app_conf.run.host}:{app_conf.run.port}")
    uvicorn.run(
        "main:app",
        host=app_cfg.RUN.host,
        port=app_cfg.RUN.port,
        reload=app_cfg.RUN.reload,
    )
