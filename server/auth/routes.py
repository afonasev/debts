from http import HTTPStatus
from typing import Optional

from fastapi import APIRouter

from ..db import User
from ..errors import NotFoundError, WrongPasswordError
from ..utils import save_unique_object
from .schemas import UserIn, UserOut
from .utils import create_access_token, hash_password, verify_password

router = APIRouter()


@router.post('/token', response_model=UserOut)
def create_token(user: UserIn) -> UserOut:
    db_user = _get_user(user)
    _verify_password(user, db_user)
    return UserOut(
        id=db_user.id, email=db_user.email, token=create_access_token(db_user)
    )


@router.post(
    '/users', response_model=UserOut, status_code=HTTPStatus.CREATED.value
)
def create_user(user_in: UserIn) -> UserOut:
    db_user = _create_user(user_in)
    return UserOut(
        id=db_user.id, email=db_user.email, token=create_access_token(db_user)
    )


def _verify_password(user: UserIn, db_user: User) -> None:
    if not verify_password(
        user.password.get_secret_value(), db_user.password_hash
    ):
        raise WrongPasswordError


def _get_user(user: UserIn) -> User:
    db_user: Optional[User] = User.query.filter_by(
        email=user.email
    ).one_or_none()

    if not db_user:
        raise NotFoundError

    return db_user


def _create_user(user_in: UserIn) -> User:
    db_user = User(
        email=user_in.email,
        password_hash=hash_password(user_in.password.get_secret_value()),
    )
    save_unique_object(db_user)
    return db_user
