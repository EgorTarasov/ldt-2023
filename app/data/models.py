import datetime
from sqlalchemy import (
    Boolean,
    ForeignKey,
    Integer,
    String,
    DateTime,
    Date,
    Column,
    Table,
)
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import relationship, mapped_column, Mapped
import json

from app.data.database import Base


class User(Base):
    __tablename__ = "users"
    """
    role_id:
    0 - Наставник -> mentor
    1 - Куратор -> curator
    2 - Кадр -> hr
    3 - Кандидат -> candidate
    4 - Стажер -> intern
    """

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String)
    policy_agreed: Mapped[bool] = mapped_column(Boolean, default=True)
    phone: Mapped[str] = mapped_column(String, nullable=True)
    fio: Mapped[str] = mapped_column(String)
    birthday: Mapped[datetime.date] = mapped_column(Date)
    gender: Mapped[str] = mapped_column(String, nullable=True)
    role_id: Mapped[int] = mapped_column(Integer, default=3)  # TODO add enum
    first_access: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=datetime.datetime.now()
    )
    last_access: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=datetime.datetime.now()
    )
    last_ip: Mapped[str] = mapped_column(String, default="127.0.0.1")
    active: Mapped[bool] = mapped_column(Boolean, default=True)

    enrolments = relationship("UserEnrolment", back_populates="user")

    vacancies = relationship(
        "Vacancy", back_populates="hr", primaryjoin="User.id==Vacancy.hr_id"
    )

    intern_application = relationship(
        "InternApplication",
        back_populates="user",
        primaryjoin="User.id==InternApplication.id",
        uselist=False,
    )

    recieved_feedbacks = relationship(
        "Feedback",
        back_populates="sender",
        primaryjoin="User.id==Feedback.sender_id",
    )
    sent_feedbacks = relationship(
        "Feedback",
        back_populates="target",
        primaryjoin="User.id==Feedback.target_id",
    )

    # vacany_enrolments = relationship(
    #     "VacancyEnrolment",
    #     back_populates="user",
    #     primaryjoin="User.id==VacancyEnrolment.user_id",
    # )

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, role_id={self.role_id})>"


class Feedback(Base):
    __tablename__ = "feedback"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    sender_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    target_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    text: Mapped[str] = mapped_column(String)

    sender = relationship(
        "User", foreign_keys=[sender_id], primaryjoin="User.id==Feedback.sender_id"
    )
    target = relationship(
        "User", foreign_keys=[target_id], primaryjoin="User.id==Feedback.target_id"
    )

    def __repr__(self):
        return f"<Feedback(sender_id={self.sender_id}, target_id={self.target_id}, text={self.text})>"


class Event(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String)
    date_time: Mapped[datetime.date] = mapped_column(Date)

    enrolments = relationship("UserEnrolment", back_populates="event")


class UserEnrolment(Base):
    __tablename__ = "user_enrolments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    event_id: Mapped[int] = mapped_column(Integer, ForeignKey("events.id"))
    status: Mapped[str] = mapped_column(String)
    role: Mapped[str] = mapped_column(String)

    user = relationship("User", back_populates="enrolments")
    event = relationship("Event", back_populates="enrolments")


class InternApplication(Base):
    __tablename__ = "intern_applications"

    id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), primary_key=True)
    course: Mapped[str] = mapped_column(String)
    education: Mapped[str] = mapped_column(String)
    resume: Mapped[str] = mapped_column(String)
    citizenship: Mapped[str] = mapped_column(String)
    graduation_date: Mapped[datetime.date] = mapped_column(Date)

    user = relationship(
        "User",
        back_populates="intern_application",
        primaryjoin="User.id==InternApplication.id",
    )

    def __repr__(self):
        return f"<InternApplication(id={self.id}, course={self.course}, education={self.education}, resume={self.resume}, citizenship={self.citizenship}, graduation_date={self.graduation_date})>"


# class Vacancy_Tag(Base):
#     __tablename__ = "vacancy_tag"

#     tag_id: Mapped[int] = mapped_column(
#         Integer, ForeignKey("tags.id"), primary_key=True
#     )
#     vacancy_id: Mapped[int] = mapped_column(Integer, ForeignKey("vacancies.id"))


class Vacancy(Base):
    __tablename__ = "vacancies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(String)
    # test_id: Mapped[int] = mapped_column(Integer, ForeignKey("tests.id"))
    hr_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    start_date: Mapped[datetime.datetime] = mapped_column(DateTime)
    end_date: Mapped[datetime.datetime] = mapped_column(DateTime)
    test: Mapped[str] = mapped_column(String)
    requirements: Mapped[str] = mapped_column(JSON)

    hr = relationship(
        "User",
        back_populates="vacancies",
        primaryjoin="User.id==Vacancy.hr_id",
    )

    tags = relationship(
        "Tag",
        back_populates="vacancies",
        secondary="vacancy_tags",
    )

    def __repr__(self):
        return f"<Vacancy(id={self.id}, title={self.title}, description={self.description}, hr_id={self.hr_id}, start_date={self.start_date}, end_date={self.end_date}, test={self.test}, requirements={self.requirements})>"

    # vacancy_enrolments = relationship(
    #     "VacancyEnrolment",
    #     back_populates="vacancy",
    #     primaryjoin="Vacancy.id==VacancyEnrolment.vacany_id",
    # )


class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, unique=True)

    vacancies = relationship("Vacancy", back_populates="tags", secondary="vacancy_tags")

    def __repr__(self):
        return f"<Tag(id={self.id}, name={self.name})>"


vacancy_tags = Table(
    "vacancy_tags",
    Base.metadata,
    Column("tag_id", Integer, ForeignKey("vacancies.id")),
    Column("vacancy_id", Integer, ForeignKey("tags.id")),
)

# class VacancyEnrolment(Base):
#     __tablename__ = "vacancy_enrolments"

#     id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
#     user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
#     vacany_id: Mapped[int] = mapped_column(Integer, ForeignKey("vacancies.id"))
#     status: Mapped[str] = mapped_column(String)
#     results: Mapped[dict] = mapped_column(JSONB)

#     user = relationship(
#         "User",
#         back_populates="vacancy_enrolments",
#         primaryjoin="User.id==VacancyEnrolment.user_id",
#     )
#     vacancy = relationship(
#         "Vacancy",
#         back_populates="vacancy_enrolments",
#         primaryjoin="Vacancy.id==VacancyEnrolment.vacany_id",
#     )


# class Test(Base):
#     __tablename__ = "tests"
