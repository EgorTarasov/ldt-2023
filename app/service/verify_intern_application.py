import datetime
from app.data import schemas
from app.data import models
from app.utils.logging import log


def verify(
    intern_application: schemas.InternApplication, db_user: models.User
) -> schemas.InternApplication:
    """Автоматическая верификация заявки на стажировку на основые параметры

    Args:
        intern_application (schemas.InternApplication): _description_
        db_user (models.User): _description_

    Returns:
        schemas.InternApplication: _description_
    """
    log.debug(f"intern_application: {intern_application}")
    verification = (
        (intern_application.citizenship == "RU")
        and (18 <= datetime.datetime.now().year - db_user.birthday.year <= 35)
        and (
            intern_application.graduation_date.year - datetime.datetime.now().year <= 1
        )
    )
    log.debug(f"ctizenship: {intern_application.citizenship == 'RU'}")
    log.debug(
        f"age: {18 <= datetime.datetime.now().year - db_user.birthday.year <= 35}"
    )
    log.debug(
        f"graduation: {intern_application.graduation_date.year - datetime.datetime.now().year <= 1}"
    )
    log.debug(verification)

    intern_application.status = "verified" if verification else "unverified"
    return intern_application
