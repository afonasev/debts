import pytest
from starlette.testclient import TestClient

from server.asgi import app
from server.db import Base, engine, session
from server.utils import create_access_token

from .factories import OperationFactory, PersonFactory, UserFactory


@pytest.fixture()
def client():
    with TestClient(app) as _client:
        yield _client


@pytest.fixture(autouse=True)
def _init_db():
    Base.metadata.create_all(engine)  # type: ignore
    yield
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
