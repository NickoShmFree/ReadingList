from typing import TYPE_CHECKING, Annotated

from fastapi import APIRouter, Depends, Path

from schemas import ItemCreateSchema, ItemResponseSchema
from api.dependencies.get_services import (
    get_item_service,
    get_current_user_service,
)
from schemas import CurrentUserSchema, ItemUpdateSchema

if TYPE_CHECKING:
    from services import ItemService
    from api.dependencies.get_current_user import CurrentUser


router = APIRouter(prefix="/item", tags=["Item"])


@router.post("/add")
async def add(
    item_service: Annotated["ItemService", Depends(get_item_service)],
    current_user_service: Annotated["CurrentUser", Depends(get_current_user_service)],
    item: ItemCreateSchema,
) -> ItemResponseSchema:
    """
    Создает новую книгу (статью) для текущего аутентифицированного пользователя.

    Позволяет пользователю добавить книгу или статью в свой список чтения
    с указанием статуса, приоритета, заметок и тегов.

    Args:
        item_service: Сервис для работы со списками чтения.
        current_user_service: Сервис для получения текущего пользователя.
        item: Данные для создания списка чтения.

    Returns:
        ItemResponseSchema: Созданный список чтения с присвоенным ID.
    """
    current_user: CurrentUserSchema = await current_user_service.get_user_by_token()
    return await item_service.add(current_user.id, item)


@router.get(
    "/dd/{item_id}",
    response_model=ItemResponseSchema,
    summary="Получить элемент по ID",
    description="Возвращает элемент списка чтения по его идентификатору.",
    responses={
        200: {"description": "Элемент найден"},
        404: {"description": "Элемент не найден"},
        410: {"description": "Элемент удален"},
    },
)
async def get_item(
    item_id: Annotated[int, Path(description="ID элемента", gt=0)],
    item_service: Annotated["ItemService", Depends(get_item_service)],
) -> ItemResponseSchema:
    """
    Получить конкретный элемент списка чтения.

    Args:
        item_id: Идентификатор элемента
        item_service: Сервис для работы с элементами

    Returns:
        Элемент списка чтения

    Raises:
        HTTPException 404: Если элемент не найден
    """
    return await item_service.get_item(item_id)


@router.delete(
    "/{item_id}",
    response_model=ItemResponseSchema,
    summary="Мягкое удаление элемента",
    description="""
    Помечает элемент как удаленный (мягкое удаление).
    Элемент остается в базе данных, но не отображается в обычных запросах.
    """,
    responses={
        200: {"description": "Элемент помечен как удаленный"},
        404: {"description": "Элемент не найден"},
        403: {"description": "Нет доступа к элементу"},
    },
)
async def soft_delete_item(
    item_id: Annotated[int, Path(description="ID элемента для удаления", gt=0)],
    item_service: Annotated["ItemService", Depends(get_item_service)],
    current_user_service: Annotated["CurrentUser", Depends(get_current_user_service)],
) -> ItemResponseSchema:
    """
    Мягкое удаление элемента списка чтения.

    Элемент помечается как удаленный, но остается в базе данных.
    Может быть восстановлен администратором или через отдельный эндпоинт.

    Args:
        item_id: ID элемента для удаления
        item_service: Сервис для работы с элементами
        current_user: Текущий аутентифицированный пользователь

    Returns:
        Информация об удалении

    Raises:
        HTTPException 404: Если элемент не найден
        HTTPException 403: Если элемент принадлежит другому пользователю
        HTTPException 410: Если элемент уже удален
    """
    current_user: CurrentUserSchema = await current_user_service.get_user_by_token()
    return await item_service.del_item(item_id=item_id, user_id=current_user.id)


@router.patch(
    "",
    response_model=ItemResponseSchema,
    summary="Частично обновить элемент",
    description="Частично обновляет данные элемента списка чтения.",
    responses={
        200: {"description": "Элемент обновлен"},
        404: {"description": "Элемент не найден"},
        403: {"description": "Нет доступа к элементу"},
        410: {"description": "Элемент удален"},
    },
)
async def update_item(
    new_item: ItemUpdateSchema,
    item_service: Annotated["ItemService", Depends(get_item_service)],
    current_user_service: Annotated["CurrentUser", Depends(get_current_user_service)],
) -> ItemResponseSchema:
    """
    Частично обновить элемент списка чтения.

    Args:
        item_id: ID элемента для обновления
        update_data: Частичные данные для обновления
        item_service: Сервис для работы с элементами
        current_user: Текущий аутентифицированный пользователь

    Returns:
        Обновленный элемент
    """
    current_user: CurrentUserSchema = await current_user_service.get_user_by_token()
    return await item_service.update_item(new_item=new_item, user_id=current_user.id)
