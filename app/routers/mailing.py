from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.data import crud, models, schemas
from app.data.constants import UserRole, MailingType
from app.dependencies import get_db, current_user
from app.utils.logging import log


router = APIRouter(prefix="/mailing", tags=["mailing"])


@router.post("/", response_model=schemas.Mailing)
async def create_mailing(
    mailing_data: schemas.MailingCreate,
    db: Session = Depends(get_db),
    sender: models.User = Depends(current_user),
) -> schemas.Mailing:
    if sender.role_id == UserRole.candidate or sender.role_id == UserRole.intern:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    target: models.User | None = None
    if mailing_data.target_id is not None:
        target = crud.get_user(db, mailing_data.target_id)
    elif mailing_data.target_email is not None:
        target = crud.get_user_by_email(db, mailing_data.target_email)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You should specify target_id or target_email",
        )

    if target is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Target user not found"
        )

    db_mailing: models.Mailing = crud.create_mailing(db, mailing_data, sender, target)
    return schemas.Mailing.from_orm(db_mailing)


@router.get("/{mailing_type}", response_model=list[schemas.Mailing] | None)
async def get_mailings(
    mailing_type: MailingType,
    limit: Annotated[int, Query(..., ge=0, le=100)] = 10,
    offset: Annotated[int, Query(..., ge=0)] = 0,
    db: Session = Depends(get_db),
    db_user: models.User = Depends(current_user),
) -> list[schemas.Mailing] | None:
    db_mailings: list[models.Mailing] | None = None

    if mailing_type == MailingType.sent:
        db_mailings = crud.get_sent_mailings(db, db_user, limit, offset)
    elif mailing_type == MailingType.received:
        db_mailings = crud.get_recieved_mailings(db, db_user, limit, offset)
    if db_mailings is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No mailings found"
        )
    return (
        [schemas.Mailing.from_orm(db_feedback) for db_feedback in db_mailings]
        if db_mailings
        else None
    )