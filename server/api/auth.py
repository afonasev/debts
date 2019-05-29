from http import HTTPStatus

from fastapi import APIRouter
from sqlalchemy.exc import IntegrityError
from starlette.responses import JSONResponse

from ..config import config
from ..db import User, session
from ..errors import DuplicateError, NotFoundError, WrongPasswordError
from ..models import UserIn, UserOut
from ..utils import create_access_token, hash_password, verify_password

router = APIRouter()


def _response_with_token(user: User, status_code: int) -> JSONResponse:
    response = JSONResponse(
        {'id': user.id, 'email': user.email}, status_code=status_code
    )
    response.set_cookie(
        key=config.ACCESS_TOKEN_COOKIE,
        value=create_access_token(user),
        secure=True,
        httponly=True,
    )
    return response


@router.post('/token', response_model=UserOut)
def create_token(user: UserIn) -> JSONResponse:
    with session() as s:
        db_user = s.query(User).filter_by(email=user.email).one_or_none()

        if not db_user:
            raise NotFoundError

        if not verify_password(
            user.password.get_secret_value(), db_user.password_hash
        ):
            raise WrongPasswordError

        return _response_with_token(db_user, HTTPStatus.OK)


@router.post(
    '/users', response_model=UserOut, status_code=HTTPStatus.CREATED.value
)
def create_user(user_in: UserIn) -> JSONResponse:
    with session() as s:
        user = User(
            email=user_in.email,
            password_hash=hash_password(user_in.password.get_secret_value()),
        )

        s.add(user)

        try:
            s.commit()
        except IntegrityError:
            raise DuplicateError

        return _response_with_token(user, HTTPStatus.CREATED)
