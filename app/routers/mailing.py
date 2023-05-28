from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Path, Query
from sqlalchemy.orm import Session
from app.data import crud, models, schemas
from app.data.constants import (
    UserRole,
    InternApplicationStatus,
    MailingTemplate,
    MailingSubjects
)
from app.dependencies import get_db, current_user
from app.service import mailing_service
from app.utils.logging import log


router = APIRouter(prefix="/mailing", tags=["mailing"])


@router.post("/links")
async def create_mailing_links(
    links_data: dict[str, str],
    db: Session = Depends(get_db),
    db_user: models.User = Depends(current_user),
) -> list[dict[str, int | str]]:
    if db_user.role != UserRole.curator:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    db_links = crud.create_mailing_links(db, links_data)
    return [{"title": link.title, "link": link.link} for link in db_links]


@router.post("/send/school_invite", response_model=list[schemas.Mailing] | None)
async def create_school_invite_mailing(
    school_link: str = Query("", min_length=1, max_length=255),
    db: Session = Depends(get_db),
    sender: models.User = Depends(current_user),
) -> list[schemas.Mailing] | None:
    # FIXME: если есть много трекок, то надо определять каким пользователям, какие треки отправить
    if sender.role != UserRole.curator:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    intern_applications = crud.get_all_intern_applications(
        db, limit=1_000_000, offset=0, status=InternApplicationStatus.approved
    )
    if not school_link:
        school_link = crud.get_mailing_link(db, "school_invite", sender)
        if school_link is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="School link not found",
            )
        school_link = school_link.link

    mailings = [
        crud.create_mailing(db, sender, ia.user, MailingSubjects.school_invite)
        for ia in intern_applications
    ]

    for mailing in mailings:
        template_data = {
            "intern_name": mailing.target.fio,
            "link": school_link,
        }
        mailing_service.send_mailing(
            mailing, MailingTemplate.school_invite, template_data
        )

    return (
        [schemas.Mailing.from_orm(mailing) for mailing in mailings]
        if mailings
        else None
    )


@router.post("/send/{event_id}")
async def create_event_invite_mailing(
    event_id: int = Path(),
    db: Session = Depends(get_db),
    sender: models.User = Depends(current_user),
):
    if sender.role != UserRole.curator:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    event_link = f"http://0.0.0.0:8000/events/{event_id}"
