from typing import Optional
from pydantic import BaseModel


class UserBase(BaseModel):
    username: str
    email: Optional[str]


class UserCreat(UserBase):
    password: str


class UserRes(UserBase):
    id: int
    is_active: str

    class Config:
        orm_mode = True
