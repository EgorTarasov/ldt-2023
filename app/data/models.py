import datetime
from sqlalchemy import Boolean, ForeignKey, Integer, String, DateTime, Date
from sqlalchemy.orm import relationship, mapped_column, Mapped

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
