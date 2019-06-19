from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class Operation(BaseModel):
    value: Decimal
    description: str


class OperationIn(Operation):
    pass


class OperationOut(Operation):
    id: int
    person_id: int
    created: datetime
