import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from app.utils.country import get_country_code
from sqlalchemy.orm import Session
from app.data import crud, models, schemas
from app.data.constants import (
    UserRole,
    InternApplicationStatus,
    InternApplicationParameters,
)
from app.dependencies import get_db, current_user
from app.utils.settings import settings
from app.utils.logging import log
from app.service.verify_intern_application import verify


router = APIRouter(prefix="/intern_application", tags=["intern_application"])


@router.post(
    "/my", response_model=schemas.InternApplication, status_code=status.HTTP_201_CREATED
)
async def create_application(
    intern_application_data: schemas.InternApplicationCreate,
    db: Session = Depends(get_db),
    db_user: models.User = Depends(current_user),
) -> schemas.InternApplication:
    """
    Создание заявки на участие в проекте (для кандидата)
    """
    intern_application = verify(
        schemas.InternApplication(
            id=db_user.id, status="unverified", **intern_application_data.dict()
        ),
        db_user,
    )
    db_application = crud.create_intern_application(db, intern_application)

    return schemas.InternApplication.from_orm(db_application)


@router.get("/my")
async def get_application(
    db_user: models.User = Depends(current_user),
):
    """
    Просмотр заполненной заявки (для кандидата)
    """
    db_application: models.InternApplication | None = crud.get_intern_application(
        db_user
    )

    if db_application is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Application not found"
        )

    return schemas.InternApplication.from_orm(db_application)


@router.get("/stats")
async def get_stats(
    parameters: InternApplicationParameters = Query(...),
    db: Session = Depends(get_db),
    db_user: models.User = Depends(current_user),
):  # -> dict[str, int]:
    """
    Получение статистики по заявкам (для куратора)
    """
    if not db_user.role == UserRole.curator:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    try:
        data = crud.get_intern_application_stats(db, parameters)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e)
    return {x[0]: x[1] for x in data}


@router.get("/all", response_model=list[schemas.InternApplication] | None)
async def get_all_intern_applications(
    offset: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    intern_application_status: InternApplicationStatus = InternApplicationStatus.verified,
    db: Session = Depends(get_db),
    db_user: models.User = Depends(current_user),
) -> list[schemas.InternApplication] | None:
    """
    Получение списка заявок по статусу:

    intern_application_status:
    verified - прошедшие автоматическую проверку
    unverified - не прошедшие автоматическую проверку
    approved - одобренные куратором
    rejected - отклоненные куратором

    """
    if not db_user.role == UserRole.curator:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

    db_applications = crud.get_all_intern_applications(
        db, offset, limit, intern_application_status
    )
    return (
        [
            schemas.InternApplication.from_orm(db_application)
            for db_application in db_applications
        ]
        if db_applications
        else None
    )


@router.get("/{id}", response_model=schemas.InternApplication | None)
async def get_intern_application_by_id(
    id: int,
    db: Session = Depends(get_db),
    db_user: models.User = Depends(current_user),
) -> schemas.InternApplication | None:
    """
    Получение заявки по id (для куратора)
    """
    log.debug(f"get_intern_application_by_id: {id} by {db_user}")
    if not db_user.role == UserRole.curator.value:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    try:
        db_application = crud.get_intern_application_by_id(db, id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Application not found"
        )

    return (
        schemas.InternApplication.from_orm(db_application) if db_application else None
    )


# endpoint for approving intern applications (curator only)
@router.post("/approve", response_model=schemas.InternApplication | None)
async def approve_intern_application(
    intern_application_id: int = Query(..., ge=1),
    db: Session = Depends(get_db),
    db_user: models.User = Depends(current_user),
):
    """
    Одобрение заявки (для куратора)
    """
    if not db_user.role == UserRole.curator.value:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    try:
        db_intern_application = crud.update_intern_application_status(
            db, intern_application_id, InternApplicationStatus.approved
        )
        return schemas.InternApplication.from_orm(db_intern_application)
    except ValueError:
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Application not found"
        )
