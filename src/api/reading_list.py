from typing import TYPE_CHECKING, Annotated

from fastapi import APIRouter, Depends

from schemas import ItemCreateSchema, ItemResponseSchema
from api.dependencies.get_services import (
    get_reading_list_service,
    get_current_user_service,
)
from schemas.user import CurrentUserSchema


if TYPE_CHECKING:
    from services import ItemService
    from api.dependencies.get_current_user import CurrentUser

router = APIRouter(prefix="/reading-list", tags=["Reading List"])


@router.post("/add")
async def add(
    reading_list_service: Annotated["ItemService", Depends(get_reading_list_service)],
    current_user_service: Annotated["CurrentUser", Depends(get_current_user_service)],
    item: ItemCreateSchema,
) -> ItemResponseSchema:
    """
    Создает новую книгу (статью) для текущего аутентифицированного пользователя.

    Позволяет пользователю добавить книгу или статью в свой список чтения
    с указанием статуса, приоритета, заметок и тегов.

    Args:
        reading_list_service: Сервис для работы со списками чтения.
        current_user_service: Сервис для получения текущего пользователя.
        item: Данные для создания списка чтения.

    Returns:
        ItemResponseSchema: Созданный список чтения с присвоенным ID.
    """
    current_user: CurrentUserSchema = await current_user_service.get_user_by_token()
    return await reading_list_service.add(current_user.id, item)
