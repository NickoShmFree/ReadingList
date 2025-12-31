from typing import TYPE_CHECKING, Annotated, Optional
from datetime import date

from fastapi import APIRouter, Depends, Query

from schemas import ItemResponseSchema, ItemFilters
from api.dependencies.get_services import get_item_service
from db.services_db import SortOrder, SortBy
from db.models.items import ItemPriorityEnum, ItemKindEnum, ItemStatusEnum

if TYPE_CHECKING:
    from services import ItemService


router = APIRouter(prefix="/items", tags=["Items"])


@router.get(
    "",
    response_model=list[ItemResponseSchema],
    summary="Получить элементы пользователя",
    description="""
    Возвращает элементы текущего пользователя с комплексной фильтрацией.
    
    Поддерживает:
    - Фильтрацию по статусу, типу, приоритету
    - Поиск по подстроке в названии
    - Фильтрацию по тегам (OR - элементы с ЛЮБЫМ из указанных тегов)
    - Фильтрацию по диапазону дат создания
    - Пагинацию
    """,
    responses={
        200: {"description": "Список элементов"},
        400: {"description": "Некорректные параметры фильтрации"},
    },
)
async def get_items(
    item_service: Annotated["ItemService", Depends(get_item_service)],
    # Базовые фильтры
    status: Annotated[
        Optional[ItemStatusEnum],
        Query(description="Фильтр по статусу (planned/reading/done)"),
    ] = None,
    kind: Annotated[
        Optional[ItemKindEnum], Query(description="Фильтр по типу (book/article)")
    ] = None,
    priority: Annotated[
        Optional[ItemPriorityEnum],
        Query(description="Фильтр по приоритету (low/normal/high)"),
    ] = None,
    # Поиск по названию
    title_search: Annotated[
        Optional[str],
        Query(
            description="Поиск по подстроке в названии (регистронезависимый)",
            min_length=2,
            max_length=50,
        ),
    ] = None,
    # Фильтрация по тегам (OR логика)
    tag_names: Annotated[
        Optional[list[str]],
        Query(
            description="Фильтр по тегам (элементы с ЛЮБЫМ из указанных тегов). "
            "Можно указать несколько тегов: &tags=python&tags=programming",
            max_length=10,  # максимум 10 тегов для фильтрации
        ),
    ] = None,
    # Диапазон дат
    created_from: Annotated[
        Optional[date],
        Query(
            description="Начало диапазона дат создания (включительно). "
            "Формат: YYYY-MM-DD",
            examples=["2024-01-01"],
        ),
    ] = None,
    created_to: Annotated[
        Optional[date],
        Query(
            description="Конец диапазона дат создания (включительно). "
            "Формат: YYYY-MM-DD",
            examples=["2024-12-31"],
        ),
    ] = None,
    # Дополнительные опции
    include_deleted: Annotated[
        bool, Query(description="Включать удаленные элементы", include_in_schema=False)
    ] = False,
    sort_by: SortBy = Query(SortBy.CREATED_AT),
    sort_order: SortOrder = Query(SortOrder.ASC),
    # Пагинация
    offset: Annotated[
        int, Query(description="Смещение для пагинации", ge=0, examples=[0])
    ] = 0,
    limit: Annotated[
        int,
        Query(description="Лимит элементов на странице", ge=1, le=100, examples=[20]),
    ] = 20,
) -> list[ItemResponseSchema]:
    """
    Получить элементы списка чтения с комплексной фильтрацией.

    Args:
        item_service: Сервис для работы с элементами
        current_user: Текущий аутентифицированный пользователь
        status: Фильтр по статусу
        kind: Фильтр по типу
        priority: Фильтр по приоритету
        title_search: Поиск по подстроке в названии
        tags: Фильтр по тегам (OR логика - любой из)
        created_from: Начало диапазона дат создания
        created_to: Конец диапазона дат создания
        include_deleted: Включать удаленные элементы
        sort_by: Поле для сортировки
        sort_order: Порядок сортировки
        offset: Смещение для пагинации
        limit: Количество элементов на странице

    Returns:
        Список элементов, удовлетворяющих фильтрам

    Example:
        ```bash
        # Все книги с высоким приоритетом, созданные в 2024
        GET /items?kind=book&priority=high&created_from=2024-01-01&created_to=2024-12-31

        # Элементы с тегами python ИЛИ javascript
        GET /items?tags=python&tags=javascript

        # Поиск по названию "чистый" с сортировкой по приоритету
        GET /items?title_search=чистый&sort_by=priority&sort_order=desc
        ```
    """

    items = await item_service.get_items(
        filters=ItemFilters(
            status=status,
            kind=kind,
            priority=priority,
            title_search=title_search,
            tag_names=tag_names,
            created_from=created_from,
            created_to=created_to,
            include_deleted=include_deleted,
            sort_by=sort_by,
            sort_order=sort_order,
            offset=offset,
            limit=limit,
        ),
    )
    return items
