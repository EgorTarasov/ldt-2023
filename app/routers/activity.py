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


@router.get("/scores", response_model=list[schemas.EventScore] | None)
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

    return (
        [
            schemas.EventScore.from_orm(db_event_score)
            for db_event_score in db_events_scores
        ]
        if db_events_scores
        else None
    )


@router.get("/candidates/all", response_model=list[schemas.CandidateActivity] | None)
async def get_candidates_activity(
    db: Session = Depends(get_db),
    db_user: models.User = Depends(current_user),
    offset: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
) -> list[schemas.CandidateActivity] | None:
    """
    Получение данных о всех кандидатах (для куратора)
    """
    if db_user.role != UserRole.curator:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    db_candidates_scores = crud.get_candidates_scores(db, limit, offset)
    if db_candidates_scores is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return (
        [
            schemas.CandidateActivity(**{
                "user_id": db_candidate_score[0],
                "overall_score": db_candidate_score[1],
                "max_score": db_candidate_score[2],
            })
            for db_candidate_score in db_candidates_scores
        ]
        if db_candidates_scores
        else None
    )


# @router.get("/cadidates/{candidate_id}", response_model=list[schemas.CandidateActivity] | None)
# async def get_candidate_activity_by_id(
#     candidate_id: int = Path(..., ge=1),
#     db: Session = Depends(get_db),
#     db_user: models.User = Depends(current_user),
# ) -> list[schemas.CandidateActivity] | None:
#     """
#     Получение данных о конкретном кандидате (для куратора)
#     """
#     if db_user.role != UserRole.curator:
#         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

#     db_candidate_score = crud.get_candidate_score_by_id(db, candidate_id)
#     if db_candidate_score is None:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

#     return [
#         schemas.CandidateActivity(**{
#             "user_id": db_candidate_score[0],
            
#         }) for event in db_candidate_score
#     ]
