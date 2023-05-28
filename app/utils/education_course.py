import pandas as pd
from pydantic import BaseModel
import datetime
from app.data import schemas


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
    tracks = [schemas.EducationalTrack(**row) for row in df.to_dict(orient="records")]
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
        schemas.StudentTrackInfo(
            fio=fio,
            course=course,
            scores=[i for i in scores],
        )
        for fio, course, scores in student_data
    ]

    df2 = pd.read_excel(file_name, sheet_name="Программа развития")
    event_dates = df2.columns.tolist()
    event_dates = event_dates[2:-3]
    if any(not isinstance(name, datetime.datetime) for name in event_dates):
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
        schemas.EventCreate(title=title, start_date=date, max_score=int(score))
        for title, date, score in events
    ]

    return tracks, students, edu_events
