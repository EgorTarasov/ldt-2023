from typing import Optional, Any
from datetime import date, datetime, time


from pydantic import BaseModel, EmailStr, SecretStr, Json, AnyHttpUrl


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


# region Feedback


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


# endregion

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


# region Test


class TestBase(BaseModel):
    title: str
    description: str


class Test(TestBase):
    id: int

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {"id": 1, "title": "Загаловок", "description": "описание"}
        }


# endregion Test


# region Tag
class TagBase(BaseModel):
    name: str


class TagCreate(TagBase):
    class Config:
        schema_extra = {"example": {"name": "Тэг"}}


class Tag(TagBase):
    id: int

    class Config:
        orm_mode = True
        schema_extra = {"example": {"id": 1, "name": "Тэг"}}


# endregion Tag

# region Vacancy


class VacancyBase(BaseModel):
    title: str
    description: str
    start_date: datetime
    end_date: datetime
    requirements: Optional[dict[str, Any]]
    test: Optional[Test | AnyHttpUrl] = AnyHttpUrl("https://127.0.0.1", scheme="https")


class VacancyCreate(VacancyBase):
    tags: Optional[list[TagCreate]]

    class Config:
        schema_extra = {
            "example": {
                "title": "Название вакансии",
                "description": "Описание",
                "start_date": datetime(2023, 6, 15, 0, 0, 0),
                "end_date": datetime(2023, 6, 30, 0, 0, 0),
                "tags": [
                    {
                        "name": "Стажер",
                    },
                    {
                        "name": "Шахтер",
                    },
                ],
                "requirements": {"some_requirement": "some_value"},
                "test_url": "https://127.0.0.1",
            }
        }


class Vacancy(VacancyBase):
    id: Optional[int | None] = None
    tags: list[Tag]
    hr_id: int

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "id": 1,
                "title": "Название вакансии",
                "description": "Описание",
                "start_date": datetime(2023, 6, 15, 0, 0, 0),
                "end_date": datetime(2023, 6, 30, 0, 0, 0),
                "tags": ["Стажер", "Шахтер"],
                "test": "https://127.0.0.1",
            }
        }


# endregion


# region Event


# class EventBase(BaseModel):
#     title: str
#     start_time: datetime


# class EventCreate(EventBase):
#     class Config:
#         schema_extra = {
#             "example": {
#                 "title": "Название события",
#                 "start_time": datetime(2023, 6, 15, 0, 0, 0),
#             }
#         }


# class Event(EventBase):
#     id: Optional[int | None] = None

#     class Config:
#         orm_mode = True
#         schema_extra = {
#             "example": {
#                 "id": 1,
#                 "title": "Название события",
#                 "start_time": datetime(2023, 6, 15, 0, 0, 0),
#             }
#         }


# endregion Event

# region Mailing


class MailingBase(BaseModel):
    target_id: int | None
    subject: str
    message: str
    time_sent: datetime = datetime.now()


class MailingCreate(MailingBase):
    target_email: EmailStr | None

    class Config:
        schema_extra = {
            "example": {
                "target_id": 2,
                "subject": "Тема письма",
                "message": "Сообщение",
                "target_email": "test1@test.com",
            },
        }


class Mailing(MailingBase):
    id: Optional[int | None] = None
    sender_id: int

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "sender_id": 1,
                "target_id": 2,
                "subject": "Тема письма",
                "message": "Сообщение",
                "target_email": "test1@test.com",
            }
        }


# endregion Mailing
