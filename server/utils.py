from datetime import datetime, timedelta
from typing import Any, List, Type, cast

import jwt
from fastapi import Cookie
from passlib.context import CryptContext
from pydantic import BaseModel

from .config import config
from .db import User
from .errors import ForbiddenError, UnauthorizedError

JWT_ACCESS_SUBJECT = 'access'
JWT_ALGORITHM = 'HS256'

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


def hash_password(password: str) -> str:
    return cast(str, pwd_context.hash(password))


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return cast(bool, pwd_context.verify(plain_password, hashed_password))


def create_access_token(user: User) -> str:
    delta = timedelta(seconds=config.ACCESS_TOKEN_LIFE_TIME)
    jwt_payload = {
        'id': user.id,
        'email': user.email,
        'exp': datetime.utcnow() + delta,
        'sub': JWT_ACCESS_SUBJECT,
    }
    token = jwt.encode(jwt_payload, config.SECRET_KEY, algorithm=JWT_ALGORITHM)
    return token.decode()


def check_access_token(
    user_id: int, token: str = Cookie(..., alias=config.ACCESS_TOKEN_COOKIE)
) -> None:
    try:
        payload = jwt.decode(
            token, config.SECRET_KEY, algorithms=[JWT_ALGORITHM]
        )
    except jwt.PyJWTError:
        raise UnauthorizedError

    if user_id != payload['id']:
        raise ForbiddenError


def obj_to_model(model: Type[BaseModel], obj: Any) -> BaseModel:
    fields = {}
    for field in model.schema()['properties'].keys():
        fields[field] = getattr(obj, field)
    return model(**fields)


def objs_to_models(model: Type[BaseModel], objs: List[Any]) -> List[BaseModel]:
    return [obj_to_model(model, i) for i in objs]
