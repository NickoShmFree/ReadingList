from typing import TYPE_CHECKING, Annotated

from fastapi import APIRouter, Depends, Response

from api.dependencies.get_services import get_auth_service
from schemas import UserCreateSchema, UserLoginSchema

if TYPE_CHECKING:
    from services import AuthService

router = APIRouter(prefix="/auth", tags=["AUTH"])


@router.post(
    "/register",
    responses={
        200: {"description": "Пользователь успешно зарегистрирован"},
        400: {"description": "Пользователь с такой почтой уже зарегистрирован"},
    },
    summary="Регистрация нового пользователя",
    description="""
    Создает новую учетную запись пользователя.
    
    Требования к данным:
    - Email должен быть валидным и уникальным
    - Пароль должен содержать минимум 8 символов
    - Пароль должен содержать буквы в верхнем и нижнем регистре, а также цифры
    
    После успешной регистрации пользователь может войти в систему.
    """,
)
async def register(
    user: UserCreateSchema,
    auth_service: Annotated["AuthService", Depends(get_auth_service)],
) -> dict[str, str]:
    """
    Регистрация нового пользователя.

    Создает учетную запись пользователя с указанными данными.
    Пароль должен быть не менее 8 символов и содержать буквы в разных регистрах и цифры.

    Args:
        user: Данные для регистрации нового пользователя.
        auth_service: Сервис аутентификации.

    Returns:
        "msg": "Новый пользователь зарегистрирован.".

    Raises:
        HTTPException 400: Если пользователь с таким email уже существует.
        HTTPException 400: При ошибках валидации данных.
    """
    await auth_service.register(user)
    return {"msg": "Новый пользователь зарегистрирован."}


@router.post(
    "/login",
    responses={
        201: {"description": "Login successful"},
        401: {"description": "Invalid credentials"},
    },
)
async def login(
    credentials: UserLoginSchema,
    auth_service: Annotated["AuthService", Depends(get_auth_service)],
) -> Response:
    """
    Аутентификация пользователя.

    Проверяет учетные данные пользователя и устанавливает JWT-токены
    в HTTP-only cookies для последующих авторизованных запросов.

    Args:
        credentials: Данные для входа (email и пароль).
        auth_service: Сервис аутентификации, инжектированный через зависимость.

    Returns:
        HTTP-ответ с установленными cookies:
        - `access_token`: JWT токен для доступа к защищенным эндпоинтам
        - `refresh_token`: JWT токен для обновления access токена

    Raises:
        HTTPException 401: Если email или пароль неверны.
        HTTPException 400: При ошибках валидации входных данных.
    """
    return await auth_service.login(credentials)


@router.post(
    "/logout",
    responses={
        204: {"description": "Logout successful"},
        401: {"description": "Not authenticated"},
    },
)
async def logout(
    auth_service: Annotated["AuthService", Depends(get_auth_service)],
) -> Response:
    """
    Выход пользователя из системы.

    Удаляет авторизационные cookies (access и refresh токены).
    После вызова этого эндпоинта пользователь должен снова войти в систему
    для доступа к защищенным ресурсам.

    Args:
        auth_service: Сервис аутентификации, инжектированный через зависимость.

    Returns:
        HTTP-ответ с очищенными авторизационными cookies.
        Статус код: 204 No Content.
    """
    return await auth_service.logout()
