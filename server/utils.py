import asyncio
from functools import partial, wraps
from typing import TYPE_CHECKING, Any, Awaitable, Callable

from sqlalchemy.exc import IntegrityError

from .errors import DuplicateError

if TYPE_CHECKING:
    from .db import Base

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
