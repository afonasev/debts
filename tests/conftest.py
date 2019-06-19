import logging
from contextlib import contextmanager

import pytest
from starlette.testclient import TestClient

from server.app import create_app
from server.auth.utils import create_access_token
from server.db import Base, engine, session

from .factories import OperationFactory, PersonFactory, UserFactory

sa_logger = logging.getLogger('sqlalchemy.engine.base.Engine')


@contextmanager
def disable_sql_log():
    sa_logger.setLevel(logging.ERROR)
    yield
    sa_logger.setLevel(logging.INFO)


@pytest.fixture(autouse=True)
def app():
    return create_app(init_logging=False)


@pytest.fixture()
def client(app):
    with TestClient(app) as _client:
        yield _client


@pytest.fixture(autouse=True)
def _init_db():
    with disable_sql_log():
        Base.metadata.create_all(engine)  # type: ignore

    yield

    with disable_sql_log():
        session.remove()
        Base.metadata.drop_all(engine)  # type: ignore


@pytest.fixture()
def user():
    return UserFactory()


@pytest.fixture()
def person(user):
    return PersonFactory(user_id=user.id)


@pytest.fixture()
def operation(person):
    return OperationFactory(person_id=person.id)


@pytest.fixture()
def access_token(user):
    return create_access_token(user)


@pytest.fixture(autouse=True)
def headers(mocker, access_token):
    return {'Authorization': f'Bearer {access_token}'}
