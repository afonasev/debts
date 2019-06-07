from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, EmailStr, SecretStr


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
