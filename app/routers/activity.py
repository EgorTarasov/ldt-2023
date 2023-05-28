"""
Модуль "Активность" кандидатов

Реализует следующий функционал:
- Получение мероприятий по образовательному треку   
- Получение оценок по мероприятию
- Получение требований для прохождения трека
"""
import string
import random
from typing import Annotated
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    Response,
    Query,
    Path,
    Body,
)

from sqlalchemy.orm import Session
from app.data import crud, models, schemas
from app.data.constants import UserRole, MailingTemplate, MailingSubjects
from app.dependencies import get_db, current_user
from app.service.auth import get_hashed_user
from app.utils.logging import log
from app.service import vacancy_service, mailing_service
from app.utils.settings import settings


router = APIRouter(prefix="/activity", tags=["activity"])


@router.get("/events", response_model=list[schemas.EventDto] | None)
async def get_events(
    db: Session = Depends(get_db),
    db_user: models.User = Depends(current_user),
    offset: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
) -> list[schemas.EventDto] | None:
    """
    Получение мероприятий по образовательному треку (для кандидата)
    """
    if db_user.role != UserRole.candidate:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    db_events: list[models.Event] | None = crud.get_events(db, limit, offset)
    if db_events is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return (
        [schemas.EventDto.from_orm(db_event) for db_event in db_events]
        if db_events
        else None
    )


@router.get("/events/scores", response_model=list[schemas.EventScore] | None)
async def get_events_scores(
    db: Session = Depends(get_db),
    db_user: models.User = Depends(current_user),
    offset: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
) -> list[schemas.EventScore] | None:
    """
    Получение оценок по мероприятиям (для кандидата)
    """
    if db_user.role != UserRole.candidate:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    db_events_scores = crud.get_events_scores(db, db_user, limit, offset)
    if db_events_scores is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return [schemas.EventScore.from_orm(db_event_score) for db_event_score in db_events_scores] if db_events_scores else None


@router.get("/candidates")
async def get_candidates_activity(
    db: Session = Depends(get_db),
    db_user: models.User = Depends(current_user),
    offset: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
):
    """
    Получение данных о всех кандидатах (для куратора)
    """
    if db_user.role != UserRole.curator:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    db_candidates_scores = crud.get_candidates_scores(db, limit, offset)
    if db_candidates_scores is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return {candidate[1]: {"id": candidate[0], "score": candidate[2], "max_score": candidate[3]} for candidate in db_candidates_scores}


@router.get("/cadidates/{candidate_id}")
async def get_candidate_activity_by_id(
    candidate_id: int = Path(..., ge=1),
    db: Session = Depends(get_db),
    db_user: models.User = Depends(current_user),
):
    """
    Получение данных о конкретном кандидате (для куратора)
    """
    if db_user.role != UserRole.curator:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    db_candidate_score = crud.get_candidate_score_by_id(db, candidate_id)
    if db_candidate_score is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return [{"event_id": score[0], "event_title": score[1], "score": score[2], "max_score": score[3]} for score in db_candidate_score]
