from contextlib import closing, contextmanager
from datetime import datetime
from decimal import Decimal
from typing import Any, Iterator, List

import sqlalchemy as sa
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy.orm import sessionmaker

from .config import config

engine = sa.create_engine(config.DATABASE)
session_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@contextmanager
def session(*args: Any, **kwargs: Any) -> Iterator[sa.orm.Session]:
    with closing(session_factory(*args, **kwargs)) as _session:
        try:
            yield _session
        except Exception:
            _session.rollback()
            raise
        else:
            _session.commit()


@as_declarative()
class Base:
    id: int = sa.Column(sa.Integer, primary_key=True)
    created: bool = sa.Column(sa.DateTime, index=True, default=datetime.utcnow)

    @declared_attr
    def __tablename__(cls) -> str:  # noqa:N805
        return cls.__name__.lower()  # type: ignore


class DeletableMixin:
    deleted: datetime = sa.Column(sa.DateTime, index=True)


class User(Base):
    email: str = sa.Column(sa.String, unique=True)
    password_hash: str = sa.Column(sa.String, nullable=False)

    persons: List['Person'] = sa.orm.relationship(
        'Person', backref='user', order_by='Person.balance'
    )

    def __init__(self, email: str, password_hash: str) -> None:
        self.email = email
        self.password_hash = password_hash


class Person(Base, DeletableMixin):
    name: str = sa.Column(sa.String, nullable=False, index=True)
    balance: Decimal = sa.Column(sa.DECIMAL, nullable=False, default=0)
    user_id: int = sa.Column(sa.ForeignKey(User.id), nullable=False)

    operations: List['Operation'] = sa.orm.relationship(
        'Operation', backref='person', order_by='Operation.created'
    )

    __table_args__ = (sa.UniqueConstraint('user_id', 'name'),)

    def __init__(self, user_id: int, name: str, balance: Decimal) -> None:
        self.user_id = user_id
        self.name = name
        self.balance = balance


class Operation(Base, DeletableMixin):
    value: Decimal = sa.Column(sa.DECIMAL, nullable=False)
    description: str = sa.Column(sa.String, nullable=False)
    person_id: int = sa.Column(sa.ForeignKey(Person.id), nullable=False)

    def __init__(
        self, person_id: int, value: Decimal, description: str
    ) -> None:
        self.person_id = person_id
        self.value = value
        self.description = description
