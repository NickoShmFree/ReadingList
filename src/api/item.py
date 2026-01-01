from typing import TYPE_CHECKING, Annotated

from fastapi import APIRouter, Depends, status, Path

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


@router.post(
    "/",
    response_model=ItemResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Создать новый элемент",
    description="""
    Создает новый элемент (книгу или статью) в списке чтения пользователя.
    
    ### Параметры:
    - **title**: Название элемента (обязательно, до 100 символов)
    - **kind**: Тип элемента - "книга" или "статья"
    - **status**: Статус чтения - "планирую прочитать", "читаю", "прочитал"
    - **priority**: Приоритет - "низкий", "средний", "высокий"
    - **notes**: Заметки (до 2500 символов)
    - **tags**: Список тегов (опционально)
    
    ### Особенности:
    - Автоматически назначается текущая дата создания
    - Теги создаются, если их еще нет у пользователя
    - Пользователь может иметь только одного владельца элемента
    """,
    responses={
        201: {"description": "Элемент успешно создан"},
        401: {"description": "Пользователь не аутентифицирован"},
        422: {"description": "Ошибка валидации данных"},
    },
)
async def create_item(
    item_service: Annotated["ItemService", Depends(get_item_service)],
    current_user_service: Annotated["CurrentUser", Depends(get_current_user_service)],
    item: ItemCreateSchema,
) -> ItemResponseSchema:
    """
    Создает новую книгу или статью для текущего аутентифицированного пользователя.

    Args:
        item_service: Сервис для работы со списками чтения
        current_user_service: Сервис для получения текущего пользователя
        item: Данные для создания элемента

    Returns:
        ItemResponseSchema: Созданный элемент с присвоенным ID

    Raises:
        HTTPException 401: Если пользователь не аутентифицирован
        HTTPException 422: При ошибках валидации данных
    """
    current_user: CurrentUserSchema = await current_user_service.get_user_by_token()
    return await item_service.create_item(current_user.id, item)


@router.get(
    "/{item_id}",
    response_model=ItemResponseSchema,
    summary="Получить элемент по ID",
    description="""
    Возвращает элемент списка чтения по его идентификатору.
    
    ### Условия доступа:
    - Элемент не должен быть удален (is_deleted=False)
    
    ### Возвращаемые данные:
    - Полная информация об элементе
    - Список связанных тегов
    - Даты создания и обновления
    """,
    responses={
        200: {"description": "Элемент найден и возвращен"},
        404: {"description": "Элемент не найден"},
        410: {"description": "Элемент удален"},
    },
)
async def get_item(
    item_id: Annotated[int, Path(description="ID элемента", gt=0, examples=[1])],
    item_service: Annotated["ItemService", Depends(get_item_service)],
) -> ItemResponseSchema:
    """
    Получить конкретный элемент списка чтения.

    Args:
        item_id: Идентификатор элемента (должен быть больше 0)
        item_service: Сервис для работы с элементами
        current_user_service: Сервис для получения текущего пользователя

    Returns:
        Элемент списка чтения с тегами

    Raises:
        HTTPException 401: Если пользователь не аутентифицирован
        HTTPException 403: Если элемент принадлежит другому пользователю
        HTTPException 404: Если элемент не найден
        HTTPException 410: Если элемент удален
    """
    return await item_service.get_item(item_id=item_id)


@router.patch(
    "/",
    response_model=ItemResponseSchema,
    summary="Частично обновить элемент",
    description="""
    Частично обновляет данные элемента списка чтения.
    
    ### Особенности:
    - Передается новая модель, проверяется на наличие изменений
    - Найденные изменения вносятся в БД
    - При обновлении тегов происходит сравнение со старыми тегами
    - Автоматически обновляется поле updated_at
    
    ### Поддерживаемые поля для обновления:
    - title (строка, до 100 символов)
    - kind ("книга" или "статья")
    - status ("планирую прочитать", "читаю", "прочитал")
    - priority ("низкий", "средний", "высокий")
    - notes (строка, до 2500 символов)
    - tags (список строк)
    
    ### Обработка тегов:
    - Новые теги создаются автоматически
    - Неиспользуемые теги удаляются из связи с элементом
    - Теги остаются в системе для других элементов
    """,
    responses={
        200: {"description": "Элемент успешно обновлен"},
        401: {"description": "Пользователь не аутентифицирован"},
        403: {"description": "Нет доступа к элементу"},
        404: {"description": "Элемент не найден"},
        410: {"description": "Элемент удален"},
        422: {"description": "Ошибка валидации данных"},
    },
)
async def update_item(
    item_new: ItemUpdateSchema,
    item_service: Annotated["ItemService", Depends(get_item_service)],
    current_user_service: Annotated["CurrentUser", Depends(get_current_user_service)],
) -> ItemResponseSchema:
    """
    Частично обновить элемент списка чтения.

    Args:
        item_id: ID элемента для обновления
        update_data: Частичные данные для обновления
        item_service: Сервис для работы с элементами
        current_user_service: Сервис для получения текущего пользователя

    Returns:
        Обновленный элемент с тегами

    Raises:
        HTTPException 401: Если пользователь не аутентифицирован
        HTTPException 403: Если элемент принадлежит другому пользователю
        HTTPException 404: Если элемент не найден
        HTTPException 410: Если элемент удален
    """
    current_user: CurrentUserSchema = await current_user_service.get_user_by_token()
    return await item_service.update_item(current_user.id, item_new)


@router.delete(
    "/{item_id}",
    response_model=ItemResponseSchema,
    summary="Мягкое удаление элемента",
    description="""
    Помечает элемент как удаленный (мягкое удаление).
    
    ### Что происходит при удалении:
    - Поле is_deleted устанавливается в True
    - Элемент остается в базе данных
    - Элемент не отображается в обычных запросах
    - Связи с тегами сохраняются
    
    ### Восстановление:
    Удаленный элемент может быть восстановлен администратором
    """,
    responses={
        200: {"description": "Элемент помечен как удаленный"},
        401: {"description": "Пользователь не аутентифицирован"},
        403: {"description": "Нет доступа к элементу"},
        404: {"description": "Элемент не найден"},
        410: {"description": "Элемент уже удален"},
    },
)
async def soft_delete_item(
    item_id: Annotated[
        int, Path(description="ID элемента для удаления", gt=0, examples=[1])
    ],
    item_service: Annotated["ItemService", Depends(get_item_service)],
    current_user_service: Annotated["CurrentUser", Depends(get_current_user_service)],
) -> ItemResponseSchema:
    """
    Мягкое удаление элемента списка чтения.

    Args:
        item_id: ID элемента для удаления
        item_service: Сервис для работы с элементами
        current_user_service: Сервис для получения текущего пользователя

    Returns:
        Информация об удаленном элементе

    Raises:
        HTTPException 401: Если пользователь не аутентифицирован
        HTTPException 403: Если элемент принадлежит другому пользователю
        HTTPException 404: Если элемент не найден
        HTTPException 410: Если элемент уже удален
    """
    current_user: CurrentUserSchema = await current_user_service.get_user_by_token()
    return await item_service.soft_delete_item(item_id=item_id, user_id=current_user.id)
