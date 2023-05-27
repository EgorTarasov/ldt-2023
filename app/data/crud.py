from sqlalchemy import func, text, desc, or_
from sqlalchemy.orm import Session
from app.utils.logging import log
from app.data.constants import UserRole, MentorStatus

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
    db_user.role = user.role if user.role else db_user.role
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


def update_user_mentor_vacancy(
    db: Session, user: models.User, vacancy_id: int, mentor_id: int
) -> models.User:
    db_vacancy = (
        db.query(models.Vacancy).filter(models.Vacancy.id == vacancy_id).one_or_none()
    )
    db_mentor = db.query(models.User).filter(models.User.id == mentor_id).one_or_none()
    log.debug(f"Vacancy: {db_vacancy}")
    log.debug(f"Mentor: {db_mentor}")
    if db_vacancy is None or db_mentor is None:
        raise Exception("Not found")

    db_offer = models.MentorVacancyOffer(
        mentor_id=db_mentor.id, vacancy_id=db_vacancy.id
    )
    db.add(db_offer)
    db.commit()
    db.refresh(db_offer)

    return db_mentor


def update_user_accept_offer(
    db: Session, mentor: models.User, vacancy_id: int
) -> models.User:
    db_offer = (
        db.query(models.MentorVacancyOffer).filter(
            (models.MentorVacancyOffer.vacancy_id == vacancy_id)
        )
    ).one_or_none()

    if db_offer is None:
        raise Exception("offer not found")

    db_vacancy = (
        db.query(models.Vacancy).filter(models.Vacancy.id == vacancy_id).one_or_none()
    )
    if db_vacancy is None:
        raise Exception("Vacancy not found")
    db_vacancy.mentor = mentor

    db_offer.mentor_status = MentorStatus.active.value
    db_offer.mentor = mentor
    db.commit()
    db.refresh(db_offer)

    return mentor


def get_users_available_mentors(
    db: Session, offset: int, limit: int
) -> list[models.User] | None:
    # count user mentor_vacancies

    db_data = (
        db.query(models.User)
        .filter(
            (models.User.role == UserRole.mentor.value)
            & (~models.User.mentor_vacancies.any())
        )
        .offset(offset)
        .limit(limit)
        .all()
    )

    log.debug(f"Available mentors: {db_data}")
    return db_data


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


def get_all_tags(db: Session) -> list[tuple[str, int]]:
    # get ten most popular tags
    data = (
        db.query(models.Tag.name, func.count(models.Tag.name).label("count"))
        .join(models.Vacancy.tags)
        .group_by(models.Tag.name)
        .order_by(desc("count"))
        .limit(10)
        .all()
    )
    log.debug(f"tags: {data}")

    return [tuple(i) for i in data]


def get_all_cities(db: Session) -> list[str] | None:
    # get ten most popular cities in vacancies by splitted city field by comma
    data = (
        db.query(
            func.split_part(models.Vacancy.address, ",", 1).label("city"),
            func.count(func.split_part(models.Vacancy.address, ",", 1)).label("count"),
        )
        .group_by("city")
        .order_by(desc("count"))
        .limit(10)
        .all()
    )
    log.debug(f"cities: {data}")
    return [i[0] for i in data]


def get_all_organisations(db: Session) -> list[str] | None:
    # get ten most popular organisations in vacancies
    data = (
        db.query(
            models.Vacancy.organisation,
            func.count(models.Vacancy.organisation).label("count"),
        )
        .group_by(models.Vacancy.organisation)
        .order_by(desc("count"))
        .limit(10)
        .all()
    )
    log.debug(f"organisations: {data}")
    return [i[0] for i in data]


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


def get_vacancies(
    db: Session, filters: schemas.VacancyFilters, offset: int, limit: int
) -> list[models.Vacancy]:

    data = filters.dict()

    log.debug(f"filters: {data}")
    if data["organisations"] is None:
        data["organisations"] = []
    if data["tags"] is None:
        data["tags"] = []

    if not any(data.values()):
        return db.query(models.Vacancy).offset(offset).limit(limit).all()
    db_vacancies = (
        db.query(models.Vacancy)
        .join(models.Vacancy.tags)
        .filter(
            or_(
                models.Tag.name.in_(data["tags"]),
                models.Vacancy.organisation.in_(data["organisations"]),
                models.Vacancy.address.ilike(f"%{data['city']}%"),
            )
        )
        .offset(offset)
        .limit(limit)
        .all()
    )

    log.debug(f"vacancies: {db_vacancies}")
    return db_vacancies


def delete_vacancy(db: Session, vacancy_id: int):
    db.query(models.Vacancy).filter(models.Vacancy.id == vacancy_id).delete()
    db.commit()


# endregion Vacancy

# region Mailing


def create_mailing(
    db: Session,
    mailing: schemas.MailingCreate,
    sender: models.User,
    target: models.User,
) -> models.Mailing:
    db_mailing = models.Mailing(**mailing.dict(exclude={"target_email"}))

    db_mailing.sender = sender
    db_mailing.target = target

    db.add(db_mailing)
    db.commit()
    db.refresh(db_mailing)
    return db_mailing


def get_sent_mailings(
    db: Session, db_user: models.User, limit: int, offset: int
) -> list[models.Mailing] | None:
    return (
        db.query(models.Mailing)
        .filter(models.Mailing.sender_id == db_user.id)
        .offset(offset)
        .limit(limit)
        .all()
    )


def get_recieved_mailings(
    db: Session, db_user: models.User, limit: int, offset: int
) -> list[models.Mailing] | None:
    return (
        db.query(models.Mailing)
        .filter(models.Mailing.target_id == db_user.id)
        .offset(offset)
        .limit(limit)
        .all()
    )


# endregion Mailing
