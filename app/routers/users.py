from typing import Annotated
from fastapi import APIRouter, Cookie, Depends, HTTPException, status, Response, Request
from sqlalchemy.orm import Session
from app.data import crud, models, schemas
from app.dependencies import get_db
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


@router.post("/", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
async def create_user(
    request: Request,  # TODO: add middleware to write last ip address
    response: Response,
    user_data: schemas.UserCreate,
    db: Annotated[Session, None] = Depends(get_db),
) -> schemas.User:
    """
    request.client.host - получить ip адрес
    """
    db_user: models.User = crud.create_user(db, auth.get_hashed_user(user_data))

    response.set_cookie(
        key="access_token",
        value=auth.create_access_token(data={"sub": user_data.email}),
        httponly=True,
        max_age=60 * 60 * 24 * 30,
    )

    return schemas.User.from_orm(db_user)


@router.post("/login")
async def login(
    response: Response,
    user_data: schemas.UserLogin,
    db: Annotated[Session, None] = Depends(get_db),
):
    log.debug("Data")
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
    return {"message": "login success"}


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
    access_token: str | None = Cookie(None),
    db: Session = Depends(get_db),
) -> schemas.User:
    if not access_token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    db_user = await auth.get_current_user(db, access_token)
    log.debug(db_user)
    return schemas.User.from_orm(db_user)


@router.put("/")
async def update_user(
    user_data: schemas.User,
    access_token: str | None = Cookie(None),
    db: Session = Depends(get_db),
):
    if not access_token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    db_user = await auth.get_current_user(db, access_token)  # нужно ли это тут?
    crud.update_user(db, user_data)
