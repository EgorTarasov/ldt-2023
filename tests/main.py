import httpx
from enum import Enum

import pandas as pd
from pydantic import BaseModel
from datetime import datetime
import asyncio


class EventBase(BaseModel):
    title: str
    start_date: datetime
    max_score: int


class EventCreate(EventBase):
    ...

    class Config:
        schema_extra = {
            "example": {
                "title": "Название события",
                "start_date": datetime(2023, 6, 15, 0, 0, 0),
                "max_score": 2,
            }
        }


class EventDto(EventBase):
    id: int

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "id": 1,
                "title": "Название события",
                "start_date": datetime(2023, 6, 15, 0, 0, 0),
                "max_score": 2,
            }
        }


class EducationalTrack(BaseModel):
    name: str
    required_pass_rate: float


class StudentTrackInfo(BaseModel):
    fio: str
    course: str
    scores: list[int]


# file_name = "../static/Программа развития.xlsx"


def process_file(file_name: str):
    df = pd.read_excel(file_name, sheet_name="Программа развития (инфо)")
    df = df.iloc[1:]
    # drop 3 column
    df = df.drop(df.columns[2], axis=1)
    # rename columns as name and required_pass_rate
    df = df.rename(
        columns={
            "Прохождение программы развития стажеров явялется обязательной частью для получения сертификата об окончании стажировки в Правительстве Москвы.": "name",
            "Unnamed: 1": "required_pass_rate",
        }
    )
    # create list of EducationalTrack objects from rows in df
    tracks = [EducationalTrack(**row) for row in df.to_dict(orient="records")]
    df2 = pd.read_excel(file_name, sheet_name="Программа развития")
    # parsing students infro
    student_info = df2.iloc[3:, :2]

    student_scores = df2.iloc[3:, 2:-3]
    student_scores = student_scores.fillna(0)
    # replace object type to int (0)
    student_scores = student_scores.astype(int)
    student_scores = student_scores.values.tolist()

    student_info = student_info.rename(columns={"Дата": "fio", "Unnamed: 1": "course"})
    student_fio = student_info["fio"].tolist()
    student_course = student_info["course"].tolist()
    student_data = zip(student_fio, student_course, student_scores)

    students = [
        StudentTrackInfo(fio=fio, course=course, scores=scores)
        for fio, course, scores in student_data
    ]

    df2 = pd.read_excel(file_name, sheet_name="Программа развития")
    event_dates = df2.columns.tolist()
    event_dates = event_dates[2:-3]
    if any(not isinstance(name, datetime) for name in event_dates):
        raise ValueError("Column names should be dates")
    events_names = df2.iloc[0].tolist()[2:-3]
    event_max_scores = df2.iloc[1].tolist()[2:-3]
    # change event_max_scores to int and if nan to 0
    # event_max_scores = [0 if isinstance(score, float) else score for score in event_max_scores]
    # print event_max_scores types

    event_max_scores = [int(score) for score in event_max_scores]
    if len(event_max_scores) != len(event_dates) and len(event_max_scores) != len(
        events_names
    ):
        raise ValueError("Number of dates and number of max scores should be equal")

    events = zip(events_names, event_dates, event_max_scores)
    # print(*events, sep="\n")

    edu_events = [
        EventCreate(title=title, start_date=date, max_score=int(score))
        for title, date, score in events
    ]

    return tracks, students, edu_events


class UserRole(str, Enum):
    mentor = "mentor"
    curator = "curator"
    hr = "hr"
    candidate = "candidate"
    intern = "intern"


"""
1) создать hr, mentor
2) создать вакансию (hr)
3) принять менторп на вакансию (hr)
4) опубликовать вакансию (mentor)

5) создать студентов (с fio из таблицы)
"""


async def create_user(role: UserRole, email: str, password: str, fio: str):
    data = {
        "email": email,
        "phone": "+7 (999) 999-99-99",
        "gender": "М",
        "birthday": "2000-05-28",
        "fio": fio,
        "password": password,
        "role": role.value,
    }
    url = "http://0.0.0.0:8000/api/users/"
    response = httpx.post(url, json=data)

    print(response.json())


if __name__ == "__main__":
    _, students, _ = process_file("test.xlsx")
    tasks = []
    for index, student in enumerate(students):
        tasks.append(
            create_user(
                UserRole.candidate,
                f"misis.larek.deda+{index}@mail.ru",
                "test123456",
                student.fio,
            )
        )
