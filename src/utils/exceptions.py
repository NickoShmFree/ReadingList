from fastapi import HTTPException, status


class AppErrors(HTTPException):
    def __init__(
        self, status_code: int, detail: str, headers: dict[str, str] | None = None
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)

    @staticmethod
    def unauthorized(
        detail: str = "Unauthorized", headers: dict[str, str] | None = None
    ):
        return AppErrors(status.HTTP_401_UNAUTHORIZED, detail, headers)

    @staticmethod
    def bad_request(
        detail: str = "Bad request", headers: dict[str, str] | None = None
    ) -> "AppErrors":
        return AppErrors(status.HTTP_400_BAD_REQUEST, detail, headers)

    @staticmethod
    def forbidden(
        detail: str = "Forbidden", headers: dict[str, str] | None = None
    ) -> "AppErrors":
        return AppErrors(status.HTTP_403_FORBIDDEN, detail, headers)

    @staticmethod
    def not_found(
        detail: str = "Not found", headers: dict[str, str] | None = None
    ) -> "AppErrors":
        return AppErrors(status.HTTP_404_NOT_FOUND, detail, headers)

    @staticmethod
    def internal_server_error(
        detail: str = "Internal server error", headers: dict[str, str] | None = None
    ):
        return AppErrors(status.HTTP_500_INTERNAL_SERVER_ERROR, detail, headers)
