import logging

from fastapi import Depends, FastAPI
from starlette.middleware.cors import CORSMiddleware

from .api.auth import router as auth_router
from .api.operations import router as operations_router
from .api.persons import router as persons_router
from .config import config
from .db import Base, engine
from .utils import check_access


def create_app() -> FastAPI:
    app = FastAPI(title=config.PROJECT_NAME, version='1.0', docs_url='/api')

    init_routers(app)
    init_cors(app)
    init_logging()

    Base.metadata.create_all(bind=engine)  # type: ignore
    return app


def init_cors(app: FastAPI) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=['*'],
        allow_credentials=True,
        allow_methods=['GET', 'POST', 'PUT', 'DELETE'],
        allow_headers=['Content-Type'],
    )


def init_routers(app: FastAPI) -> None:
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


def init_logging() -> None:
    logging.basicConfig(
        format=config.LOGGING_FORMAT, level=config.LOGGING_LEVEL
    )
