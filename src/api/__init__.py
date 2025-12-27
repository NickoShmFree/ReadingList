from fastapi import APIRouter

from .auth import router as router_auth


router = APIRouter(prefix="/api")


router.include_router(router_auth)
