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
    db_user = models.User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# region Feedback


def get_all_feedbacks(
    db: Session, skip: int = 0, limit: int = 100
) -> list[models.Feedback] | None:
    return db.query(models.Feedback).offset(skip).limit(limit).all()


def create_feedback(db: Session, feedback: schemas.Feedback) -> models.Feedback:
    log.debug(f"Creating feedback: {feedback}")
    db_feedback = models.Feedback(**feedback.dict())
    log.debug(f"Created feedback: {db_feedback}")
    db.add(db_feedback)
    db.commit()
    db.refresh(db_feedback)
    log.debug(f"Feedback from db: {db_feedback}")
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
