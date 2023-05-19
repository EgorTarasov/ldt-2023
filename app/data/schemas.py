from typing import List, Optional
from datetime import datetime

from pydantic import BaseModel


class UserLogin(BaseModel):
    email: str
    password: str
    stay_loggedin: Optional[bool] = False


class UserBase(BaseModel):
    email: str
    phone: Optional[str] = None
    fio: str
    gender: str


class UserCreate(UserBase):
    password: str
    role_id: Optional[int]

    class Config:
        schema_extra = {
            "example": {
                "email": "test@test.com",
                "phone": "+7 (999) 999-99-99",
                "gender": "М",
                "fio": "Мисосов Михаил Михайлович",
                "password": "test123456",
            }
        }


class UserCreateHashed(UserBase):
    hashed_password: str


class User(UserBase):
    id: int
    first_access: datetime
    last_access: datetime
    last_ip: str
    active: bool
    role_id: Optional[int]

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "email": "test@test.com",
                "phone": "+7 (999) 999-99-99",
                "fio": "Мисосов Михаил Михайлович ",
                "gender": "М",
                "role_id": 0,
                "first_access": datetime.now(),
                "last_access": datetime.now(),
                "last_ip": "127.0.0.1",
                "active": True,
                "password": "string",
            }
        }


class TokenData(BaseModel):
    email: Optional[str] = None
