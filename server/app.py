import asyncio
import logging

import sentry_sdk
from context_logging import setup_log_record
from contextvars_executor import ContextVarExecutor
from fastapi import Depends, FastAPI
from sentry_asgi import SentryMiddleware
from starlette.middleware.cors import CORSMiddleware

from .auth.routes import router as auth_router
from .auth.utils import check_access
from .config import config
from .db import session_middleware
from .operations.routes import router as operations_router
from .persons.routes import router as persons_router
from .utils import context_middleware


def create_app(init_logging: bool = True) -> FastAPI:
    app = FastAPI(title=config.PROJECT_NAME, version='1.0', docs_url='/api')

    if init_logging:
        _init_logging()

    _init_context(app)
    _init_routers(app)
    _init_cors(app)
    _init_sentry(app)
    _init_db(app)

    return app


def _init_cors(app: FastAPI) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=['*'],
        allow_credentials=True,
        allow_methods=['GET', 'POST', 'PUT', 'DELETE'],
        allow_headers=['Content-Type'],
    )


def _init_routers(app: FastAPI) -> None:
    app.include_router(auth_router, prefix='/api/auth', tags=['Auth'])
    app.include_router(
        persons_router,
        prefix='/api/users',
        tags=['Persons'],
        dependencies=[Depends(check_access)],
    )
    app.include_router(
        operations_router,
        prefix='/api/users',
        tags=['Operations'],
        dependencies=[Depends(check_access)],
    )


def _init_logging() -> None:
    logging.basicConfig(
        format=config.LOGGING_FORMAT, level=config.LOGGING_LEVEL
    )

    if config.DATABASE_LOGGING_ENABLED:
        sa_logger = logging.getLogger('sqlalchemy.engine.base.Engine')
        sa_logger.setLevel(logging.INFO)

    setup_log_record()


def _init_sentry(app: FastAPI) -> None:
    if not config.SENTRY_DSN:
        return
    sentry_sdk.init()
    app.add_middleware(SentryMiddleware)


def _init_db(app: FastAPI) -> None:
    app.middleware('http')(session_middleware)


def _init_context(app: FastAPI) -> None:
    app.middleware('http')(context_middleware)
    loop = asyncio.get_event_loop()
    loop.set_default_executor(ContextVarExecutor(config.THREAD_POOL_SIZE))
