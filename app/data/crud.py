from sqlalchemy.orm import Session
from app.utils.logging import log

from . import models, schemas


def get_user(db: Session, user_id: int) -> models.User | None:
    return db.query(models.User).filter(models.User.id == user_id).one_or_none()


def get_user_by_email(db: Session, email: str) -> models.User | None:
    return db.query(models.User).filter(models.User.email == email).one_or_none()


def get_users(db: Session, skip: int = 0, limit: int = 100) -> list[models.User] | None:
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreateHashed) -> models.User:
    db_user = models.User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(db: Session, user: schemas.User) -> models.User:
    db_user = db.query(models.User).filter(models.User.id == user.id).one_or_none()
    if db_user is None:
        raise Exception("User not found")
    db_user.email = user.email
    db_user.fio = user.fio
    db_user.phone = user.phone if user.phone else db_user.phone
    db_user.role_id = user.role_id if user.role_id else db_user.role_id
    db_user.birthday = user.birthday if user.birthday else db_user.birthday
    db_user.gender = user.gender

    db_user = db.merge(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


# region Feedback


def get_all_feedbacks(
    db: Session, skip: int = 0, limit: int = 100
) -> list[models.Feedback] | None:
    return db.query(models.Feedback).offset(skip).limit(limit).all()


def create_feedback(db: Session, feedback: schemas.Feedback) -> models.Feedback:
    # log.debug(f"Creating feedback: {feedback}")
    db_feedback = models.Feedback(**feedback.dict())
    # log.debug(f"Created feedback: {db_feedback}")
    db.add(db_feedback)
    db.commit()
    db.refresh(db_feedback)
    # log.debug(f"Feedback from db: {db_feedback}")
    return db_feedback


def get_user_received_feedbacks(
    db: Session, db_user: models.User, limit: int, offset: int
) -> list[models.Feedback] | None:
    return (
        db.query(models.Feedback)
        .filter(models.Feedback.target_id == db_user.id)
        .offset(offset)
        .limit(limit)
        .all()
    )


def get_user_sent_feedbacks(
    db: Session, db_user: models.User, limit: int, offset: int
) -> list[models.Feedback] | None:
    return (
        db.query(models.Feedback)
        .filter(models.Feedback.sender_id == db_user.id)
        .offset(offset)
        .limit(limit)
        .all()
    )


def delete_feedback(db: Session, user: models.User, feedback_id: int) -> None:
    db.query(models.Feedback).filter(
        (models.Feedback.id == feedback_id) & (models.Feedback.sender_id == user.id)
    ).delete()

    db.commit()


# endregion Feedback


# region InternApplication


def create_intern_application(
    db: Session, application: schemas.InternApplication
) -> models.InternApplication:
    db_application = models.InternApplication(**application.dict())
    db.add(db_application)
    db.commit()
    db.refresh(db_application)
    return db_application


def update_intern_application(
    db: Session, user, application: schemas.InternApplication
) -> models.InternApplication:
    # FIXME: update with one line
    db_application: models.InternApplication = user.intern_application
    db_application.education = application.education
    db_application.course = application.course
    db_application.resume = application.resume
    db_application.citizenship = application.citizenship
    db_application.graduation_date = application.graduation_date

    db_application = db.merge(db_application)
    db.commit()
    db.refresh(db_application)
    return db_application


def get_intern_application(user: models.User) -> models.InternApplication | None:
    return user.intern_application


# endregion InternApplication

# region Vacancy


def create_vacancy(
    db: Session, vacancy: schemas.VacancyCreate, hr: models.User
) -> models.Vacancy:
    tags = vacancy.tags
    if tags is None:
        tags = []

    db_vacancy = models.Vacancy(
        **vacancy.dict(
            exclude={"tags"},
        ),
    )
    db_vacancy.hr = hr
    for t in tags:
        # TODO: check if we create tag in other places
        db_tag = db.query(models.Tag).filter(models.Tag.name == t.name).one_or_none()
        if db_tag is None:
            db_tag = models.Tag(**t.dict())
            db.add(db_tag)
            db.commit()
            db.refresh(db_tag)
        db_vacancy.tags.append(db_tag)

    db.add(db_vacancy)
    db.commit()
    db.refresh(db_vacancy)
    return db_vacancy


# endregion Vacancy
