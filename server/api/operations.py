from http import HTTPStatus
from typing import List, Optional

from fastapi import APIRouter

from ..db import Operation, Person, Session
from ..errors import NotFoundError
from ..models import OperationIn, OperationOut

router = APIRouter()


def _get_person(user_id: int, person_id: int) -> Person:
    db_person: Optional[Person] = Person.query.filter_by(
        id=person_id, user_id=user_id, deleted=None
    ).one_or_none()

    if not db_person:
        raise NotFoundError

    return db_person


@router.get(
    '/{user_id}/persons/{person_id}/operations',
    response_model=List[OperationOut],
)
def get_operations(user_id: int, person_id: int) -> List[Operation]:
    db_person = _get_person(user_id, person_id)

    return Operation.query.filter_by(  # type: ignore
        person_id=db_person.id, deleted=None
    ).all()


@router.post(
    '/{user_id}/persons/{person_id}/operations',
    response_model=OperationOut,
    status_code=HTTPStatus.CREATED.value,
)
def create_operation(
    user_id: int, person_id: int, operation: OperationIn
) -> Operation:
    db_person = _get_person(user_id, person_id)
    db_operation = Operation(person_id=db_person.id, **operation.dict())
    db_person.balance = Person.balance + db_operation.value
    Session.add_all([db_person, db_operation])
    Session.commit()
    return db_operation


@router.delete('/{user_id}/persons/{person_id}/operations/{operation_id}')
def delete_operation(user_id: int, person_id: int, operation_id: int) -> None:
    db_person = _get_person(user_id, person_id)

    db_operation = Operation.query.filter_by(
        person_id=db_person.id, id=operation_id, deleted=None
    ).one_or_none()

    if not db_operation:
        raise NotFoundError

    db_operation.delete()
    db_person.balance = Person.balance - db_operation.value
    Session.add_all([db_person, db_operation])
    Session.commit()
