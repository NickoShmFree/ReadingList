from fastapi import APIRouter

from .auth import router as router_auth
from .items import router as router_reading_list

router = APIRouter(prefix="/api")


router.include_router(router_auth)
router.include_router(router_reading_list)
