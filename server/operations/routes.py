from http import HTTPStatus
from typing import List, Optional, cast

from fastapi import APIRouter

from ..db import Operation, Person, session
from ..errors import NotFoundError
from .schemas import OperationIn, OperationOut

router = APIRouter()


@router.get(
    '/{user_id}/persons/{person_id}/operations',
    response_model=List[OperationOut],
)
def get_operations(user_id: int, person_id: int) -> List[Operation]:
    db_person = _get_person(user_id, person_id)

    return cast(
        List[Operation],
        Operation.query.filter_by(person_id=db_person.id, deleted=None).all(),
    )


@router.post(
    '/{user_id}/persons/{person_id}/operations',
    response_model=OperationOut,
    status_code=HTTPStatus.CREATED.value,
)
def create_operation(
    user_id: int, person_id: int, operation: OperationIn
) -> Operation:
    db_person = _get_person(user_id, person_id)
    return _create_operation(db_person, operation)


@router.delete('/{user_id}/persons/{person_id}/operations/{operation_id}')
def delete_operation(user_id: int, person_id: int, operation_id: int) -> None:
    db_person = _get_person(user_id, person_id)
    _delete_operation(db_person, operation_id)


def _get_person(user_id: int, person_id: int) -> Person:
    db_person: Optional[Person] = Person.query.filter_by(
        id=person_id, user_id=user_id, deleted=None
    ).one_or_none()

    if not db_person:
        raise NotFoundError

    return db_person


def _create_operation(db_person: Person, operation: OperationIn) -> Operation:
    db_operation = Operation(person_id=db_person.id, **operation.dict())
    db_person.balance = Person.balance + db_operation.value
    session.add_all([db_person, db_operation])
    session.commit()
    return db_operation


def _get_operation(db_person: Person, operation_id: int) -> Operation:
    db_operation: Optional[Operation] = Operation.query.filter_by(
        person_id=db_person.id, id=operation_id, deleted=None
    ).one_or_none()

    if not db_operation:
        raise NotFoundError

    return db_operation


def _delete_operation(db_person: Person, operation_id: int) -> None:
    db_operation = _get_operation(db_person, operation_id)
    db_operation.delete()
    db_person.balance = Person.balance - db_operation.value
    session.add_all([db_person, db_operation])
    session.commit()
