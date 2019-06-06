from factory import Faker
from factory.alchemy import SESSION_PERSISTENCE_COMMIT, SQLAlchemyModelFactory

from server.db import Operation, Person, Session, User


class BaseMeta:
    sqlalchemy_session = Session
    sqlalchemy_session_persistence = SESSION_PERSISTENCE_COMMIT


class UserFactory(SQLAlchemyModelFactory):
    email = Faker('email')
    password_hash = Faker('sha1')

    class Meta(BaseMeta):
        model = User


class PersonFactory(SQLAlchemyModelFactory):
    name = Faker('name')
    balance = 0

    class Meta(BaseMeta):
        model = Person


class OperationFactory(SQLAlchemyModelFactory):
    value = 10
    description = Faker('sentence')

    class Meta(BaseMeta):
        model = Operation
