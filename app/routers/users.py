from typing import Annotated
from fastapi import (
    APIRouter,
    Cookie,
    Depends,
    status,
    Response,
    Request,
    Body,
    HTTPException,
)
from sqlalchemy.orm import Session
from app.data import crud, models, schemas
from app.dependencies import get_db, current_user
from app.service import auth
from app.utils.settings import settings
from app.utils.logging import log


router = APIRouter(prefix="/users", tags=["users"])

"""
post create_user
post login
post refresh_token
delete logout
get get_user
post update_user
"""


@router.post(
    "/",
    openapi_extra=schemas.UserCreate.Config.schema_extra,
    response_model=schemas.User,
    status_code=status.HTTP_201_CREATED,
)
async def create_user(
    request: Request,  # TODO: add middleware to write last ip address
    response: Response,
    user_data: Annotated[
        schemas.UserCreate,
        Body(..., examples=schemas.UserCreate.Config.schema_extra["examples"]),
    ],
    db: Annotated[Session, None] = Depends(get_db),
) -> schemas.User:
    """
    request.client.host - получить ip адрес
    """
    try:
        db_user: models.User = crud.create_user(db, auth.get_hashed_user(user_data))

        response.set_cookie(
            key="access_token",
            value=auth.create_access_token(data={"sub": user_data.email}),
            httponly=True,
            max_age=60 * 60 * 24 * 30,
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return schemas.User.from_orm(db_user)


@router.post("/login", response_model=schemas.User)
async def login(
    response: Response,
    user_data: Annotated[
        schemas.UserLogin,
        Body(..., examples=schemas.UserLogin.Config.schema_extra["examples"]),
    ],
    db: Annotated[Session, None] = Depends(get_db),
) -> schemas.User:
    auth.authenticate_user(db, user_data)
    access_token = auth.create_access_token(data={"sub": user_data.email})
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=False,
        max_age=60 * 60 * 24 * 30,
    )

    if user_data.stay_loggedin:
        refresh_token = auth.create_refresh_token(data={"sub": user_data.email})
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=False,
            max_age=60 * 60 * 24 * 30,
        )

    db_user = crud.get_user_by_email(db, user_data.email)
    return schemas.User.from_orm(db_user)


@router.delete("/")
async def logout(
    response: Response,
    refresh_token: str | None = Cookie(None),
    access_token: str | None = Cookie(None),
):
    response.delete_cookie(
        key="refresh_token",
        httponly=False,
    )
    response.delete_cookie(
        key="access_token",
        httponly=False,
    )
    return {"message": "logout success"}


@router.get("/", response_model=schemas.User)
async def get_user(
    db_user: models.User = Depends(current_user),
) -> schemas.User:
    log.debug(db_user)
    return schemas.User.from_orm(db_user)


@router.put("/", response_model=schemas.User)
async def update_user(
    user_data: schemas.User,
    db: Session = Depends(get_db),
) -> schemas.User:
    db_user = crud.update_user(db, user_data)

    return schemas.User.from_orm(db_user)
