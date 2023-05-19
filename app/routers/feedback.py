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
)
from sqlalchemy.orm import Session
from app.data import crud, models, schemas
from app.dependencies import get_db
from app.service import auth
from app.utils.settings import settings
from app.utils.logging import log


router = APIRouter(prefix="/feedback", tags=["feedback"])


@router.get("/{feedback_type}", response_model=list[schemas.Feedback] | None)
async def get_feedbacks(
    feedback_type: str,
    limit: Annotated[int, Query(..., ge=0, le=100)] = 10,
    offset: Annotated[int, Query(..., ge=0)] = 0,
    access_token: str | None = Cookie(None),
    db: Session = Depends(get_db),
) -> list[schemas.Feedback] | None:
    if not access_token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    db_user = await auth.get_current_user(db, access_token)
    if feedback_type == "received":
        db_feedbacks = crud.get_user_received_feedbacks(db, db_user, limit, offset)
    else:
        db_feedbacks = crud.get_user_sent_feedbacks(db, db_user, limit, offset)

    return (
        [schemas.Feedback.from_orm(db_feedback) for db_feedback in db_feedbacks]
        if db_feedbacks
        else None
    )


@router.post(
    "/create", response_model=schemas.Feedback, status_code=status.HTTP_201_CREATED
)
async def create_feedback(
    feedback_data: schemas.FeedbackCreate,
    access_token: str | None = Cookie(None),
    db: Session = Depends(get_db),
) -> schemas.Feedback:
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authorized"
        )

    sender = await auth.get_current_user(db, access_token)
    target = crud.get_user(db, feedback_data.target_id)

    db_feedback = crud.create_feedback(db, feedback_data, sender.id)

    if sender.sent_feedbacks:
        sender.sent_feedbacks.append(db_feedback)
    else:
        sender.sent_feedbacks = [db_feedback]

    return schemas.Feedback.from_orm(db_feedback)
