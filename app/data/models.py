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

from app.data import schemas
from app.data.database import Base


class User(Base):
    __tablename__ = "users"
    """
    role:
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
    role: Mapped[str] = mapped_column(String, default="candidate")  # TODO add enum
    first_access: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=datetime.datetime.now()
    )
    last_access: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=datetime.datetime.now()
    )
    last_ip: Mapped[str] = mapped_column(String, default="127.0.0.1")
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    vk: Mapped[str] = mapped_column(String, nullable=True)
    telegram: Mapped[str] = mapped_column(String, nullable=True)

    enrolments = relationship("UserEnrolment", back_populates="user")

    vacancies = relationship(
        "Vacancy", back_populates="hr", primaryjoin="User.id==Vacancy.hr_id"
    )

    mentor_vacancies = relationship(
        "Vacancy", back_populates="mentor", primaryjoin="User.id==Vacancy.mentor_id"
    )

    mentor_vacancy_offers = relationship(
        "MentorVacancyOffer",
        back_populates="mentor",
        primaryjoin="User.id==MentorVacancyOffer.mentor_id",
    )

    intern_application = relationship(
        "InternApplication",
        back_populates="user",
        primaryjoin="User.id==InternApplication.id",
        uselist=False,
    )

    recieved_mailings = relationship(
        "Mailing", back_populates="target", primaryjoin="User.id==Mailing.target_id"
    )
    sent_mailings = relationship(
        "Mailing", back_populates="sender", primaryjoin="User.id==Mailing.sender_id"
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

    event_scores = relationship(
        "EventScore", back_populates="user", primaryjoin="User.id==EventScore.user_id"
    )

    external_service_links = relationship(
        "ExternalServiceLink", back_populates="creator"
    )

    # vacany_enrolments = relationship(
    #     "VacancyEnrolment",
    #     back_populates="user",
    #     primaryjoin="User.id==VacancyEnrolment.user_id",
    # )

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"


class Feedback(Base):
    """Отзывы о пользователях из модуля "обратная связь"

    Args:
        Base (_type_): _description_

    Returns:
        _type_: _description_
    """

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
    start_time: Mapped[datetime.datetime] = mapped_column(DateTime)
    max_score: Mapped[int] = mapped_column(Integer)

    scores = relationship("EventScore", back_populates="event")
    enrolments = relationship("UserEnrolment", back_populates="event")
    event_scores = relationship("EventScore", back_populates="event")


class EventScore(Base):
    __tablename__ = "event_scores"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    event_id: Mapped[int] = mapped_column(Integer, ForeignKey("events.id"))
    score: Mapped[int] = mapped_column(Integer)

    user = relationship("User", back_populates="event_scores")
    event = relationship("Event", back_populates="event_scores")

    def __repr__(self):
        return f"<EventScore(user_id={self.user_id}, event_id={self.event_id}, score={self.score})>"


class UserEnrolment(Base):
    __tablename__ = "user_enrolments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    event_id: Mapped[int] = mapped_column(Integer, ForeignKey("events.id"))
    status: Mapped[str] = mapped_column(String)

    user = relationship("User", back_populates="enrolments")
    event = relationship("Event", back_populates="enrolments")


class InternApplication(Base):
    """
    Модель заявки на стажировку
    Модуль «Заявки на стажировку»
    """

    __tablename__ = "intern_applications"

    id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), primary_key=True)
    course: Mapped[str] = mapped_column(String)  # курс обучения
    education: Mapped[str] = mapped_column(String)  # название учебного заведения
    resume: Mapped[str] = mapped_column(String)
    citizenship: Mapped[str] = mapped_column(String)
    graduation_date: Mapped[datetime.date] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String)
    city: Mapped[str] = mapped_column(String)
    """
        Статус заявки на стажировку
        unverified - заявка не прошла базовую фильтрацию
        verified - заявка прошла базовую фильтрацию
        approved - заявка одобрена куратором
        declined - заявка отклонена куратором
    """
    user = relationship(
        "User",
        back_populates="intern_application",
        primaryjoin="User.id==InternApplication.id",
    )

    def __repr__(self):
        return f"<InternApplication(id={self.id}, course={self.course}, education={self.education}, resume={self.resume}, citizenship={self.citizenship}, graduation_date={self.graduation_date}, status={self.status})>"

    @property
    def rating(requirements: schemas.VacancyRequirementsBase) -> float:
        """
        Расчет рейтинга заявки на стажировку, проверяем гражданстов РФ, закончил 3 курс бакалавриата, имеет опыт работы (модуль "Заявки на стажировку")
        """
        raise NotImplementedError


class Vacancy(Base):
    """
    Модель вакансии для Кадров (Модуль «Потребность в стажерах»)
    """

    __tablename__ = "vacancies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(String)
    # test_id: Mapped[int] = mapped_column(Integer, ForeignKey("tests.id"))
    hr_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    mentor_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=True
    )
    start_date: Mapped[datetime.datetime] = mapped_column(DateTime)
    end_date: Mapped[datetime.datetime] = mapped_column(DateTime)
    test: Mapped[str] = mapped_column(String)
    requirements: Mapped[schemas.VacancyRequirementsSpecializations] = mapped_column(
        JSON
    )
    organisation: Mapped[str] = mapped_column(String)
    coordinates: Mapped[str] = mapped_column(String)  # type str = "lat,long"
    address: Mapped[str] = mapped_column(String)  # type str = "город,улица,дом"
    """
    hidden - скрытая вакансия, не видна пользователям
    pending - на вакансию не назначен ментор, не видна пользователям
    accepted - на вакансию назначен ментор, не видна пользователям
    published - вакансия опубликована, видна пользователям
    closed - вакансия закрыта, не видна пользователям   
    """
    status: Mapped[str] = mapped_column(
        String, default="hidden"
    )  # hidden, pending, published, closed

    hr = relationship(  # у нас это человек из колонки "Блок" таблицы "Комплексы правительства москвы"
        "User",
        back_populates="vacancies",
        primaryjoin="User.id==Vacancy.hr_id",
    )

    mentor = relationship(
        "User",
        back_populates="mentor_vacancies",
        primaryjoin="User.id==Vacancy.mentor_id",
    )

    mentor_vacancy_offers = relationship(
        "MentorVacancyOffer",
        back_populates="vacancy",
        primaryjoin="Vacancy.id==MentorVacancyOffer.vacancy_id",
    )

    tags = relationship(
        "Tag",
        back_populates="vacancies",
        secondary="vacancy_tags",
    )

    def __repr__(self):
        return f"<Vacancy(id={self.id}, title={self.title}, description={self.description}, hr_id={self.hr_id}, mentor_id={self.mentor_id}, start_date={self.start_date}, end_date={self.end_date}, test={self.test}, requirements={self.requirements}, organisation={self.organisation}, coordinates={self.coordinates}, address={self.address}, status={self.status})>"

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


class MentorVacancyOffer(Base):
    __tablename__ = "mentor_vacancy_offers"

    vacancy_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("vacancies.id"), primary_key=True
    )
    mentor_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), index=True)

    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=datetime.datetime.now()
    )
    mentor_status: Mapped[str] = mapped_column(String, default="pending")

    mentor = relationship(
        "User",
        back_populates="mentor_vacancy_offers",
        primaryjoin="User.id==MentorVacancyOffer.mentor_id",
    )
    vacancy = relationship(
        "Vacancy",
        back_populates="mentor_vacancy_offers",
        primaryjoin="Vacancy.id==MentorVacancyOffer.vacancy_id",
    )

    def __repr__(self):
        return f"<MentorVacancyOffer(vacancy_id={self.vacancy_id}, mentor_status={self.mentor_status}, created_at={self.created_at})>"


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


class Mailing(Base):
    __tablename__ = "mailings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    sender_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    target_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    time_sent: Mapped[datetime.datetime] = mapped_column(DateTime)
    subject: Mapped[str] = mapped_column(String)
    message: Mapped[str] = mapped_column(String)

    sender = relationship(
        "User", back_populates="sent_mailings", primaryjoin="User.id==Mailing.sender_id"
    )
    target = relationship(
        "User",
        back_populates="recieved_mailings",
        primaryjoin="User.id==Mailing.target_id",
    )


class ExternalServiceLink(Base):
    __tablename__ = "external_service_links"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String)
    link: Mapped[str] = mapped_column(String)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id")
    )  # Пользователь который добавил ссылку

    creator = relationship("User", back_populates="external_service_links")
