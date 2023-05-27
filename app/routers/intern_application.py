from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    Query
)
from app.utils.country import get_country_code
from sqlalchemy.orm import Session
from app.data import crud, models, schemas
from app.dependencies import get_db, current_user
from app.utils.settings import settings
from app.utils.logging import log


router = APIRouter(prefix="/intern_application", tags=["intern_application"])


@router.post(
    "/my", response_model=schemas.InternApplication, status_code=status.HTTP_201_CREATED
)
async def create_application(
    application_data: schemas.InternApplicationCreate,
    db: Session = Depends(get_db),
    db_user: models.User = Depends(current_user),
) -> schemas.InternApplication:
    # TODO: 
    data = application_data.dict()
    data["id"] = db_user.id
    data["citizenship"] = get_country_code(data["citizenship"])
    intern_application = schemas.InternApplication(**data)
    db_application = crud.create_intern_application(db, intern_application)

    return schemas.InternApplication.from_orm(db_application)


@router.put("/my", response_model=schemas.InternApplication)
async def update_application(
    application_data: schemas.InternApplication,
    db: Session = Depends(get_db),
    db_user: models.User = Depends(current_user),
) -> schemas.InternApplication:
    db_application = crud.update_intern_application(db, db_user, application_data)

    return schemas.InternApplication.from_orm(db_application)


@router.get("/my")
async def get_application(
    db_user: models.User = Depends(current_user),
):
    db_application: models.InternApplication | None = crud.get_intern_application(
        db_user
    )

    if db_application is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Application not found"
        )

    return schemas.InternApplication.from_orm(db_application)


@router.get("/all", response_model=list[schemas.InternApplication] | None)
async def get_all_intern_applications(offset: int = Query(0, ge=0), limit: int = Query(10, ge=1, le=100), db: Session = Depends(get_db), db_user: models.User = Depends(current_user)) -> list[schemas.InternApplication] | None:
    """
    Get all verified intern applications (curator only)
    """
    if not db_user.is_curator:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    
    db_applications = crud.get_all_intern_applications(db, offset, limit)
    return [schemas.InternApplication.from_orm(db_application) for db_application in db_applications] if db_applications else None
    
