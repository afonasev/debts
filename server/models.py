from datetime import datetime
from decimal import Decimal
from typing import Any, List, Optional, Type, TypeVar

from pydantic import BaseModel as _BaseModel
from pydantic import EmailStr, SecretStr

T = TypeVar('T', bound=_BaseModel)


class BaseModel(_BaseModel):
    @classmethod
    def parse_many(cls: Type[T], objs: List[Any]) -> List[T]:
        return [cls.parse_one(i) for i in objs]  # type: ignore

    @classmethod
    def parse_one(cls: Type[T], obj: Any) -> T:
        fields = {}
        for field in cls.schema()['properties'].keys():
            fields[field] = getattr(obj, field)
        return cls(**fields)


class UserIn(BaseModel):
    email: EmailStr
    password: SecretStr


class UserOut(BaseModel):
    id: int
    email: EmailStr
    token: str


class Person(BaseModel):
    name: str
    balance: Optional[Decimal] = None


class PersonIn(Person):
    pass


class PersonOut(Person):
    id: int
    user_id: int
    created: datetime


class Operation(BaseModel):
    value: Decimal
    description: str


class OperationIn(Operation):
    pass


class OperationOut(Operation):
    id: int
    person_id: int
    created: datetime
