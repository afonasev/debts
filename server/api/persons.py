from http import HTTPStatus
from typing import List

from fastapi import APIRouter
from sqlalchemy.exc import IntegrityError

from ..db import Person, Session
from ..errors import DuplicateError, NotFoundError
from ..models import PersonIn, PersonOut

router = APIRouter()


@router.get('/{user_id}/persons', response_model=List[PersonOut])
def get_persons(user_id: int) -> List[Person]:
    return Person.query.filter_by(  # type: ignore
        user_id=user_id, deleted=None
    ).all()


@router.post(
    '/{user_id}/persons',
    response_model=PersonOut,
    status_code=HTTPStatus.CREATED.value,
)
def create_person(user_id: int, person: PersonIn) -> Person:
    db_person = Person(user_id=user_id, **person.dict())

    Session.add(db_person)

    try:
        Session.commit()
    except IntegrityError:
        raise DuplicateError

    return db_person


@router.delete('/{user_id}/persons/{person_id}')
def delete_person(user_id: int, person_id: int) -> None:
    db_person = Person.query.filter_by(
        user_id=user_id, id=person_id, deleted=None
    ).one_or_none()

    if not db_person:
        raise NotFoundError

    db_person.delete()
    Session.add(db_person)
    Session.commit()
