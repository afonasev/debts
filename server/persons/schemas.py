from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel


class Person(BaseModel):
    name: str
    balance: Optional[Decimal] = None


class PersonIn(Person):
    pass


class PersonOut(Person):
    id: int
    user_id: int
    created: datetime
