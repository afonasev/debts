import asyncio
from functools import partial, wraps
from typing import TYPE_CHECKING, Any, Awaitable, Callable

from context_logging import Context
from sqlalchemy.exc import IntegrityError
from starlette.requests import Request
from starlette.responses import Response

from .errors import DuplicateError

if TYPE_CHECKING:
    from .db import Base

NEXT = Callable[[Request], Awaitable[Response]]
FUNC = Callable[..., Any]


def threadpool(func: FUNC) -> FUNC:
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Awaitable[Any]:
        loop = asyncio.get_event_loop()
        callback = partial(func, *args, **kwargs)
        return loop.run_in_executor(None, callback)

    return wrapper


def save_unique_object(obj: 'Base') -> None:
    from .db import session  # cycle ref

    session.add(obj)
    try:
        session.commit()
    except IntegrityError:
        raise DuplicateError


async def context_middleware(request: Request, call_next: NEXT) -> Response:
    with Context(name=f'{request.method} {request.url}'):
        return await call_next(request)
