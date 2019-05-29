import pytest
from starlette.testclient import TestClient

from server.app import app
from server.db import Base, engine, session

from .factories import OperationFactory, PersonFactory, UserFactory
from .factories import session as factories_session


@pytest.fixture()
def client():
    with TestClient(app) as _client:
        yield _client


@pytest.fixture()
def db_session():
    with session() as s:
        yield s


@pytest.fixture(autouse=True)
def _init_db():
    Base.metadata.create_all(engine)  # type: ignore
    yield
    factories_session.remove()
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
