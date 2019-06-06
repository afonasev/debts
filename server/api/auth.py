from http import HTTPStatus

from fastapi import APIRouter
from sqlalchemy.exc import IntegrityError

from ..db import Session, User
from ..errors import DuplicateError, NotFoundError, WrongPasswordError
from ..models import UserIn, UserOut
from ..utils import create_access_token, hash_password, verify_password

router = APIRouter()


@router.post('/token', response_model=UserOut)
def create_token(user: UserIn) -> UserOut:
    db_user = User.query.filter_by(email=user.email).one_or_none()

    if not db_user:
        raise NotFoundError

    if not verify_password(
        user.password.get_secret_value(), db_user.password_hash
    ):
        raise WrongPasswordError

    return UserOut(
        id=db_user.id, email=db_user.email, token=create_access_token(db_user)
    )


@router.post(
    '/users', response_model=UserOut, status_code=HTTPStatus.CREATED.value
)
def create_user(user_in: UserIn) -> UserOut:
    db_user = User(
        email=user_in.email,
        password_hash=hash_password(user_in.password.get_secret_value()),
    )

    Session.add(db_user)

    try:
        Session.commit()
    except IntegrityError:
        raise DuplicateError

    return UserOut(
        id=db_user.id, email=db_user.email, token=create_access_token(db_user)
    )
