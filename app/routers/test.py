from typing import Annotated
from fastapi import (
    APIRouter,
    Cookie,
    Depends,
    HTTPException,
    status,
    Response,
    Request,
    Query,
    File,
)
from sqlalchemy.orm import Session
from app.data import crud, models, schemas

from app.dependencies import current_user, get_db
from app.utils.settings import settings
from app.utils.logging import log
from app.data.constants import UserRole
from app.utils.education_course import process_file


router = APIRouter(prefix="/test", tags=["test"])


@router.get("/")
async def change_role(
    db: Session = Depends(get_db),
    db_user: models.User = Depends(current_user),
    role: UserRole = Query(..., description="Role to change to"),
) -> schemas.User:
    db_user.role = role.value
    user = crud.update_user(db, db_user)

    return schemas.User.from_orm(user)


# endpoint for testing uploading excel file
@router.post("/upload")
async def upload_file(
    db: Session = Depends(get_db),
    db_user: models.User = Depends(current_user),
    file: bytes = File(...),
):
    # save file to static folder
    with open("static/test.xlsx", "wb") as f:
        f.write(file)
    # process file
    tracks, students, edu_events = process_file("static/test.xlsx")
    try:
        crud.create_students_events_scores(db, students, edu_events)
    except Exception as e:
        log.error(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
