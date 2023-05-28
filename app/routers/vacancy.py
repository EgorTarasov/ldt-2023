import string
import random
from typing import Annotated
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    Response,
    Query,
    Path,
    Body,
)

from sqlalchemy.orm import Session
from app.data import crud, models, schemas
from app.data.constants import UserRole, MailingTemplate, MailingSubjects
from app.dependencies import get_db, current_user
from app.service.auth import get_hashed_user
from app.utils.logging import log
from app.service import vacancy_service, mailing_service
from app.utils.settings import settings


router = APIRouter(prefix="/vacancy", tags=["vacancy"])


@router.post("/create", response_model=schemas.VacancyDto)
async def create_vacancy(
    vacancy_data: schemas.VacancyCreate,
    db: Session = Depends(get_db),
    db_user: models.User = Depends(current_user),
) -> schemas.VacancyDto:
    """
    Создание заявки на стажировку (для HR)
    """
    if db_user.role != UserRole.hr:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    db_vacancy: models.Vacancy = crud.create_vacancy(db, vacancy_data, db_user)
    return schemas.VacancyDto.from_orm(db_vacancy)


@router.get("/filters", response_model=schemas.VacancyFiltersAvailable)
async def get_vacancy_filters(
    db: Session = Depends(get_db),
    db_user: models.User = Depends(current_user),
) -> schemas.VacancyFiltersAvailable:
    """
    Получение доступных фильтров для вакансий
    """
    return vacancy_service.get_all_filters(db)


@router.post("/", response_model=list[schemas.VacancyDto] | None)
async def get_vacancies(
    filters: Annotated[
        schemas.VacancyFilters,
        Body(..., examples=schemas.VacancyFilters.Config.schema_extra["examples"]),
    ],
    db: Session = Depends(get_db),
    db_user: models.User = Depends(current_user),
    offset: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
) -> list[schemas.VacancyDto] | None:
    """
    Получение списка вакансий по фильтрам (для кандидата, ментора, HR, куратора)

    для кандидата - только опубликованные
    для ментора - опубликованные и принятые
    для HR - опубликованные, принятые и ожидающие (созданные HR)
    для куратора - опубликованные, принятые, ожидающие, скрытые и закрытые

    """

    vacancy_status: list[str] = []
    if db_user.role == UserRole.candidate:
        vacancy_status = ["published"]
    elif db_user.role == UserRole.mentor:
        vacancy_status = ["accepted", "published"]
    elif db_user.role == UserRole.hr:
        vacancy_status = ["accepted", "published", "pending", "hidden"]
    elif db_user.role == UserRole.curator:
        vacancy_status = ["accepted", "published", "pending", "hidden", "closed"]

    db_vacancies = crud.get_vacancies(
        db, db_user, filters, offset, limit, vacancy_status
    )
    log.debug(f"db_vacancies: {db_vacancies}")
    return (
        [schemas.VacancyDto.from_orm(vacancy) for vacancy in db_vacancies]
        if db_vacancies
        else None
    )


@router.get("/mentors", response_model=list[schemas.User] | None)
async def get_available_mentors(
    offset: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    db_user: models.User = Depends(current_user),
) -> list[schemas.User] | None:
    """
    Получение списка доступных менторов (для HR)
    """
    if db_user.role != UserRole.hr:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    db_mentors = crud.get_users_available_mentors(db, offset, limit)
    return [schemas.User.from_orm(i) for i in db_mentors] if db_mentors else None


@router.post("/mentor/apply/{vacancy_id}")
async def apply_mentor_for_vacancy(
    vacancy_id: int = Path(..., description="Vacancy id", ge=1),
    mentor_id: int = Query(..., description="Mentor id", ge=1),
    db: Session = Depends(get_db),
    db_user: models.User = Depends(current_user),
):
    """
    Назначение ментора на вакансию (для HR)
    """
    if db_user.role != UserRole.hr:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    try:
        mentor = crud.update_user_mentor_vacancy(db, db_user, vacancy_id, mentor_id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.post("/mentor/create")
async def create_mentor(
    mentor_data: schemas.MentorCreate,
    db: Session = Depends(get_db),
    db_user: models.User = Depends(current_user),
) -> schemas.User:
    """
    Создание аккаунта ментора, в случае если он не был зарегистрирован на платформе (для HR)
    """
    if db_user.role != UserRole.hr:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    password = "".join(random.choice(string.ascii_lowercase) for i in range(16))
    mentor: schemas.UserCreate = schemas.UserCreate(
        **mentor_data.dict(), password=password
    )
    mentor_create: schemas.UserCreateHashed = get_hashed_user(mentor)
    db_mentor = crud.create_mentor(db, mentor_create)

    mailing = crud.create_mailing(
        db, db_user, db_mentor, MailingSubjects.single_credentials
    )

    template_data = {
        "fio": db_mentor.fio,
        "login": db_mentor.email,
        "password": password,
        "domain": f"{settings.DOMAIN}/login",
    }
    mailing_service.send_mailing(
        mailing, MailingTemplate.single_credentials, template_data
    )

    return schemas.User.from_orm(db_mentor)


@router.get("/mentor/offers", response_model=list[schemas.MentorOfferDto] | None)
async def get_offers(
    offset: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    db_user: models.User = Depends(current_user),
) -> list[schemas.MentorOfferDto] | None:
    """
    Получение списка заявлений для начала работы (для ментора)
    """
    db_offers = crud.get_offers(db, db_user, limit, offset)
    return (
        [schemas.MentorOfferDto.from_orm(i) for i in db_offers] if db_offers else None
    )


@router.post("/mentor/offers/accept")
async def accept_vacancy_offer(
    vacancy_id: int = Query(..., description="Vacancy id", ge=1),
    db: Session = Depends(get_db),
    db_user: models.User = Depends(current_user),
):
    """
    Принятие заявки на стажировку для метора и фиксация его на вакансии (для ментора)
    """
    log.debug(f"user: {db_user}")
    log.debug(f"mentor_vacancies: {db_user.mentor_vacancies}")
    if db_user.mentor_vacancies:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You already have accepted vacancy",
        )
    try:
        mentor = crud.update_user_accept_offer(db, db_user, vacancy_id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("publish")
async def publish_vacancy(
    db: Session = Depends(get_db),
    db_user: models.User = Depends(current_user),
):
    """
    Публикация вакансии, после добавления недостающей информации (для ментора)
    """
    if db_user.role != UserRole.mentor.value:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    try:
        vacancy = crud.publish_vacancy(db, db_user)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{vacancy_id}", response_model=schemas.VacancyDto | None)
async def delete_vacancy(
    vacancy_id: int,
    db: Session = Depends(get_db),
    db_user: models.User = Depends(current_user),
) -> schemas.VacancyDto | None:
    """
    Закрытие вакансии (для HR)
    """
    if db_user.role != UserRole.hr:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    try:
        vacancy = crud.delete_vacancy(db, vacancy_id)
        return schemas.VacancyDto.from_orm(vacancy)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
