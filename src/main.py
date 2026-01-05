import logging
from logging.config import dictConfig
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from cfg.app import app_cfg
from cfg.logging import LOGGING_CONFIG

dictConfig(LOGGING_CONFIG)
logger = logging.getLogger("app")

from api import router
from db.connector import ConnectionManager


@asynccontextmanager
async def lifespan(app_: FastAPI):
    logger.info("Application starting up...")
    manager = ConnectionManager()
    manager.connect()
    logger.info("Database connection established")
    yield
    logger.info("Application shutting down...")
    await manager.disconnect()
    logger.info("Database connection closed")


app = FastAPI(
    title="Reading List",
    lifespan=lifespan,
    # docs_url=app_cfg.RUN.docs_url,
    # redoc_url=app_cfg.RUN.redoc_url,
    # openapi_url=app_cfg.RUN.openapi_url,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=app_cfg.RUN.allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
