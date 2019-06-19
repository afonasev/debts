from pydantic import BaseModel, EmailStr, SecretStr


class UserIn(BaseModel):
    email: EmailStr
    password: SecretStr


class UserOut(BaseModel):
    id: int
    email: EmailStr
    token: str
