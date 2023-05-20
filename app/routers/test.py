from typing import Annotated
from fastapi import APIRouter, Cookie, Depends, HTTPException, status, Response, Request
from sqlalchemy.orm import Session
from app.data import crud, models, schemas

from app.dependencies import current_user, get_db
from app.utils.settings import settings
from app.utils.logging import log
from app.data.constants import UserRole


router = APIRouter(prefix="/test", tags=["test"])


@router.get("/")
async def change_role(
    db: Session = Depends(get_db), db_user: models.User = Depends(current_user)
) -> schemas.User:
    db_user.role_id = UserRole.hr
    user = crud.update_user(db, db_user)

    return schemas.User.from_orm(user)
