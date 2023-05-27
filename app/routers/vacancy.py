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
from app.data.constants import UserRole
from app.dependencies import get_db, current_user
from app.utils.logging import log
from app.service import vacancy_service


router = APIRouter(prefix="/vacancy", tags=["vacancy"])


@router.post("/create", response_model=schemas.VacancyDto)
async def create_vacancy(
    vacancy_data: schemas.VacancyCreate,
    db: Session = Depends(get_db),
    db_user: models.User = Depends(current_user),
) -> schemas.VacancyDto:
    """
    Create vacancy (hr only)
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
    Get vacancy filters
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
    Get vacancies by filters
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
    Get available mentors for hr
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
    Apply mentor for vacancy (hr only)
    """
    if db_user.role != UserRole.hr:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    try:
        mentor = crud.update_user_mentor_vacancy(db, db_user, vacancy_id, mentor_id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/mentor/offers", response_model=list[schemas.MentorOfferDto] | None)
async def get_offers(
    offset: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    db_user: models.User = Depends(current_user),
) -> list[schemas.MentorOfferDto] | None:
    """
    Get offers for mentor
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
    Accept vacancy offer (mentor only)
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
    Publish vacancy (mentor only)
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
    Delete vacancy by id (hr only)
    """
    if db_user.role != UserRole.hr:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    try:
        vacancy = crud.delete_vacancy(db, vacancy_id)
        return schemas.VacancyDto.from_orm(vacancy)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
