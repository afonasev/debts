from datetime import datetime
from http import HTTPStatus
from typing import List, cast

import sqlalchemy as sa
from fastapi import APIRouter

from ..db import Operation, Person, session
from ..errors import NotFoundError
from ..models import OperationIn, OperationOut
from ..utils import objs_to_models

router = APIRouter()


def _get_person(s: sa.orm.Session, user_id: int, person_id: int) -> Person:
    db_person = (
        s.query(Person)
        .filter_by(id=person_id, user_id=user_id, deleted=None)
        .one_or_none()
    )

    if not db_person:
        raise NotFoundError

    return cast(Person, db_person)


@router.get(
    '/{user_id}/persons/{person_id}/operations',
    response_model=List[OperationOut],
)
def get_operations(user_id: int, person_id: int) -> List[OperationOut]:
    with session() as s:
        db_person = _get_person(s, user_id, person_id)

        db_operations = (
            s.query(Operation)
            .filter_by(person_id=db_person.id, deleted=None)
            .all()
        )

        return objs_to_models(OperationOut, db_operations)  # type: ignore


@router.post(
    '/{user_id}/persons/{person_id}/operations',
    response_model=OperationOut,
    status_code=HTTPStatus.CREATED.value,
)
def create_operation(
    user_id: int, person_id: int, operation: OperationIn
) -> Operation:
    with session(expire_on_commit=False) as s:
        db_person = _get_person(s, user_id, person_id)
        db_operation = Operation(person_id=db_person.id, **operation.dict())
        db_person.balance = Person.balance + db_operation.value
        s.add_all([db_person, db_operation])
        return db_operation


@router.delete('/{user_id}/persons/{person_id}/operations/{operation_id}')
def delete_operation(user_id: int, person_id: int, operation_id: int) -> None:
    with session() as s:
        db_person = _get_person(s, user_id, person_id)

        db_operation = (
            s.query(Operation)
            .filter_by(person_id=db_person.id, id=operation_id, deleted=None)
            .one_or_none()
        )

        if not db_operation:
            raise NotFoundError

        db_operation.deleted = datetime.utcnow()
        db_person.balance = Person.balance - db_operation.value
        s.add_all([db_person, db_operation])
