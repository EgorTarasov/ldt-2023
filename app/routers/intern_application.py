from typing import Annotated
from enum import Enum
from app.data.constants import FeedbackType
from fastapi import (
    APIRouter,
    Cookie,
    Depends,
    HTTPException,
    status,
    Response,
    Request,
    Query,
)
from app.utils.country import get_country_code
from sqlalchemy.orm import Session
from app.data import crud, models, schemas
from app.dependencies import get_db
from app.service import auth
from app.utils.settings import settings
from app.utils.logging import log


router = APIRouter(prefix="/intern_application", tags=["intern_application"])


@router.post(
    "/", response_model=schemas.InternApplication, status_code=status.HTTP_201_CREATED
)
async def create_application(
    application_data: schemas.InternApplicationCreate,
    access_token: str | None = Cookie(None),
    db: Session = Depends(get_db),
) -> schemas.InternApplication:
    if not access_token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    db_user = await auth.get_current_user(db, access_token)
    data = application_data.dict()
    data["id"] = db_user.id
    data["citizenship"] = get_country_code(data["citizenship"])
    intern_application = schemas.InternApplication(**data)
    db_application = crud.create_intern_application(db, intern_application)

    return schemas.InternApplication.from_orm(db_application)


@router.put("/", response_model=schemas.InternApplication)
async def update_application(
    application_data: schemas.InternApplication,
    access_token: str | None = Cookie(None),
    db: Session = Depends(get_db),
):
    if not access_token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    db_user = await auth.get_current_user(db, access_token)
    db_application = crud.update_intern_application(db, db_user, application_data)

    return schemas.InternApplication.from_orm(db_application)


@router.get("/")
async def get_application(
    access_token: str | None = Cookie(None), db: Session = Depends(get_db)
):
    if not access_token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    db_user = await auth.get_current_user(db, access_token)
    db_application: models.InternApplication | None = crud.get_intern_application(
        db_user
    )

    if db_application is None:
        raise HTTPException(status_code=404, detail="Application not found")

    return schemas.InternApplication.from_orm(db_application)
