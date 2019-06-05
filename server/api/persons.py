from datetime import datetime
from http import HTTPStatus
from typing import List

from fastapi import APIRouter
from sqlalchemy.exc import IntegrityError

from ..db import Person, session
from ..errors import DuplicateError, NotFoundError
from ..models import PersonIn, PersonOut
from ..utils import objs_to_models

router = APIRouter()


@router.get('/{user_id}/persons', response_model=List[PersonOut])
def get_persons(user_id: int) -> List[PersonOut]:
    with session() as s:
        db_persons = (
            s.query(Person).filter_by(user_id=user_id, deleted=None).all()
        )
        return objs_to_models(PersonOut, db_persons)  # type: ignore


@router.post(
    '/{user_id}/persons',
    response_model=PersonOut,
    status_code=HTTPStatus.CREATED.value,
)
def create_person(user_id: int, person: PersonIn) -> Person:
    with session(expire_on_commit=False) as s:
        db_person = Person(user_id=user_id, **person.dict())

        s.add(db_person)

        try:
            s.commit()
        except IntegrityError:
            raise DuplicateError

        return db_person


@router.delete('/{user_id}/persons/{person_id}')
def delete_person(user_id: int, person_id: int) -> None:
    with session() as s:
        db_person = (
            s.query(Person)
            .filter_by(user_id=user_id, id=person_id, deleted=None)
            .one_or_none()
        )

        if not db_person:
            raise NotFoundError

        db_person.deleted = datetime.utcnow()
        s.add(db_person)
