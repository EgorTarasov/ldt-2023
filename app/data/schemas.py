from typing import List, Optional
from datetime import date, datetime, time

from pydantic import BaseModel, EmailStr, SecretStr


class UserLogin(BaseModel):
    email: EmailStr
    password: str
    stay_loggedin: Optional[bool] = False

    class Config:
        schema_extra = {
            "example": {
                "email": "test@test.com",
                "password": "test123456",
                "stay_loggedin": False,
            }
        }


class UserBase(BaseModel):
    email: EmailStr
    phone: Optional[str] = None
    fio: str
    gender: str
    birthday: date


class UserCreate(UserBase):
    password: str
    role_id: Optional[int]

    class Config:
        schema_extra = {
            "example": {
                "email": "test@test.com",
                "phone": "+7 (999) 999-99-99",
                "gender": "М",
                "birthday": datetime.now().date(),
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
                "birthday": "2000-01-01",
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


class FeedbackBase(BaseModel):
    target_id: int
    text: str


class FeedbackCreate(FeedbackBase):
    class Config:
        schema_extra = {
            "example": {
                "target_id": 1,
                "text": "Текст отзыва",
            }
        }


class Feedback(FeedbackBase):
    id: Optional[int | None] = None
    sender_id: int

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "sender_id": 1,
                "target_id": 2,
                "text": "Текст отзыва",
            }
        }


# region Applcation


class InternApplicationBase(BaseModel):
    course: str  # TODO: add enum
    education: str  # TODO: add enum
    resume: str
    citizenship: str
    graduation_date: date


class InternApplicationCreate(InternApplicationBase):
    class Config:
        schema_extra = {
            "example": {
                "course": "Сварщик",
                "education": "Институт сварки",
                "resume": "резюме",
                "citizenship": "RU",
                "graduation_date": date(2025, 1, 1),
            }
        }


class InternApplication(InternApplicationBase):
    id: Optional[int | None] = None

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "id": 1,
                "course": "Сварщик",
                "education": "Институт сварки",
                "resume": "резюме",
                "citizenship": "RU",
                "graduation_date": "2000-01-01",
            }
        }


# endregion
