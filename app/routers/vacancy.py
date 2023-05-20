from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    Response,
    Query,
)
from sqlalchemy.orm import Session
from app.data import crud, models, schemas
from app.data.constants import UserRole
from app.dependencies import get_db, current_user
from app.utils.logging import log


router = APIRouter(prefix="/vacancy", tags=["vacancy"])


@router.post("/", response_model=schemas.Vacancy)
async def create_vacancy(
    vacancy_data: schemas.VacancyCreate,
    db: Session = Depends(get_db),
    db_user: models.User = Depends(current_user),
) -> schemas.Vacancy:
    if db_user.role_id != UserRole.hr:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    # data = vacancy_data.dict()
    # data["hr_id"] = db_user.id

    # vacancy = schemas.Vacancy(**data)

    db_vacancy: models.Vacancy = crud.create_vacancy(db, vacancy_data, db_user)
    log.debug(f"Created vacancy: {db_vacancy.tags}")
    log.debug(f"Created vacancy: {db_vacancy.requirements}")
    return schemas.Vacancy.from_orm(db_vacancy)
