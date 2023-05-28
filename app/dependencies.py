from fastapi import Cookie, HTTPException, status, Depends
from sqlalchemy.orm import Session
from app.data.database import SessionLocal
from app.service.auth import get_current_user
from app.utils.logging import log
from app.data import models


def get_db():
    with SessionLocal() as db:
        yield db


async def current_user(
    db: Session = Depends(get_db),
    access_token: str | None = Cookie(None),
    refresh_token: str | None = Cookie(None),
) -> models.User | None:
    log.debug(id(db))
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated (current_user)",
        )
    return await get_current_user(db, access_token)
