from http import HTTPStatus
from typing import Optional

from fastapi import HTTPException


class BaseError(HTTPException):
    status_code: int

    def __init__(self, detail: Optional[str] = None) -> None:
        super().__init__(status_code=self.status_code, detail=detail)


class DuplicateError(BaseError):
    status_code = HTTPStatus.BAD_REQUEST


class WrongPasswordError(BaseError):
    status_code = HTTPStatus.BAD_REQUEST


class UnauthorizedError(BaseError):
    status_code = HTTPStatus.UNAUTHORIZED


class ForbiddenError(BaseError):
    status_code = HTTPStatus.FORBIDDEN


class NotFoundError(BaseError):
    status_code = HTTPStatus.NOT_FOUND
