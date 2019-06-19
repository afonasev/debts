from http import HTTPStatus
from typing import List, Optional, cast

from fastapi import APIRouter

from ..db import Person, session
from ..errors import NotFoundError
from ..utils import save_unique_object
from .schemas import PersonIn, PersonOut

router = APIRouter()


@router.get('/{user_id}/persons', response_model=List[PersonOut])
def get_persons(user_id: int) -> List[Person]:
    return cast(
        List[Person],
        Person.query.filter_by(user_id=user_id, deleted=None).all(),
    )


@router.post(
    '/{user_id}/persons',
    response_model=PersonOut,
    status_code=HTTPStatus.CREATED.value,
)
def create_person(user_id: int, person: PersonIn) -> Person:
    db_person = Person(user_id=user_id, **person.dict())
    save_unique_object(db_person)
    return db_person


@router.delete('/{user_id}/persons/{person_id}')
def delete_person(user_id: int, person_id: int) -> None:
    db_person = _get_person(user_id, person_id)
    db_person.delete()
    session.add(db_person)
    session.commit()


def _get_person(user_id: int, person_id: int) -> Person:
    db_person: Optional[Person] = Person.query.filter_by(
        user_id=user_id, id=person_id, deleted=None
    ).one_or_none()

    if not db_person:
        raise NotFoundError

    return db_person
