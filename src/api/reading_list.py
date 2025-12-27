from typing import TYPE_CHECKING, Annotated

from fastapi import APIRouter, Depends

from schemas import ReadingListCreateSchema, ReadingListResponseSchema
from api.dependencies.get_services import (
    get_reading_list_service,
    get_current_user_service,
)
from schemas.user import CurrentUserSchema


if TYPE_CHECKING:
    from services import ReadingListService
    from api.dependencies.get_current_user import CurrentUser

router = APIRouter(prefix="/reading-list", tags=["Reading List"])


@router.post("/add")
async def add(
    reading_list_service: Annotated[
        "ReadingListService", Depends(get_reading_list_service)
    ],
    current_user_service: Annotated["CurrentUser", Depends(get_current_user_service)],
    item: ReadingListCreateSchema,
) -> ReadingListResponseSchema:
    current_user: CurrentUserSchema = await current_user_service.get_user_by_token()
    return await reading_list_service.add(current_user.id, item)
