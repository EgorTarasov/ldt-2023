from typing import Optional, Any
from datetime import date, datetime, time


from pydantic import BaseModel, EmailStr, SecretStr, Json, AnyHttpUrl, validator, Field


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
    role: Optional[str]

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
    role: Optional[str]

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "email": "test@test.com",
                "phone": "+7 (999) 999-99-99",
                "fio": "Мисосов Михаил Михайлович ",
                "gender": "М",
                "birthday": "2000-01-01",
                "role": "candidate",
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
        schema_extra = {
            "examples": {
                "example1": {
                    "value": {"name": "Программист"},
                },
                "example2": {
                    "value": {"name": "Математик"},
                },
            }
        }


class Tag(TagBase):
    id: int

    class Config:
        orm_mode = True
        schema_extra = {"example": {"id": 1, "name": "Программист"}}


# endregion Tag

# region Vacancy


class VacancyRequirementsBase(BaseModel):
    """
    #TODO: возможность получения опыта работы из резюме???
    """

    citizenship: Optional[list[str]] = ["RU, BY, KZ"]
    age: Optional[int] = 35
    experience: Optional[str]  # подразумевается опыт работы по специальности подготовки


class VacancyRequirementsSpecializations(VacancyRequirementsBase):
    education_level: Optional[dict[str, int]]
    specializations: Optional[list[str]]

    @validator("education_level", pre=True, always=True)
    def education_level_must_be_dict(cls, v):
        if not isinstance(v, dict):
            raise ValueError("Must be a dict")
        for i in v:
            if not isinstance(i, str) or not isinstance(v[i], int):
                raise ValueError("Must be a dict[str, int]")
            # check if dict key is in list ["Бакалавриат", "Магистратура", "Специалитет"]
            if i not in ["Бакалавриат", "Магистратура", "Специалитет"]:
                raise ValueError("Бакалавриат, Магистратура, Специалитет")
            if i == "Бакалавриат" and v[i] not in range(1, 5):
                raise ValueError("Бакалавриат: 1-4")
            if i == "Магистратура" and v[i] not in range(1, 3):
                raise ValueError("Магистратура: 1-2")
            if i == "Специалитет" and v[i] not in range(1, 6):
                raise ValueError("Специалитет: 1-5")

        return v

    @validator("specializations", pre=True, always=True)
    def specializations_must_be_list(cls, v):
        if not isinstance(v, list):
            raise ValueError("Must be a list")
        for i in v:
            if len(i.split(".")) != 3 or not all([i.isdigit() for i in i.split(".")]):
                raise ValueError(
                    "Код специализации должен содержать 3 числа разделенных точкой, пример: 01.03.02"
                )

        return v

    class Config:
        schmea_extra = {
            "example": {
                "citizenship": ["RU", "BY", "KZ"],
                "age": 35,
                "experience": "1 год",
                "education_level": {
                    "Бакалавриат": 3,
                    "Специалитет": 4,
                },
                "specializations": ["01.03.02", "01.03.03"],
            }
        }


class VacancyBase(BaseModel):
    title: str
    description: str
    start_date: datetime
    end_date: datetime
    requirements: Optional[VacancyRequirementsSpecializations]
    organisation: str
    address: str
    coordinates: str = "55.728291, 37.609463"  # type str = "lat,long"
    test: Optional[Any] = AnyHttpUrl("https://127.0.0.1", scheme="https")


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
                    TagCreate.Config.schema_extra["examples"][i]["value"]
                    for i in TagCreate.Config.schema_extra["examples"]
                ],
                "requirements": VacancyRequirementsSpecializations.Config.schmea_extra[
                    "example"
                ],
                "organisation": "Ларек Деда",
                "address": "Москва,Ленинский проспект,4",
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


class VacancyFiltersBase(BaseModel):
    tags: Optional[list[str]]
    organisations: Optional[list[str]]


class VacancyFiltersAvailable(VacancyFiltersBase):
    city: Optional[list[str]]


class VacancyFilters(VacancyFiltersBase):

    city: Optional[str]
    start_date: Optional[datetime | None]
    end_date: Optional[datetime | None]


class MentorOfferBase(BaseModel):
    vacancy_id: int
    mentor_id: int


class MentorOfferCreate(MentorOfferBase):
    class Config:
        schema_extra = {
            "example": {
                "mentor_id": 1,
                "vacancy_id": 1,
            }
        }


class MentorOfferDto(MentorOfferBase):
    created_at: datetime
    mentor_status: str

    class Config:
        from_orm = True
        schema_extra = {
            "example": {
                "vacancy_id": 1,
                "mentor_id": 1,
                "created_at": datetime(2023, 6, 15, 0, 0, 0),
                "mentor_status": "pending",
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
