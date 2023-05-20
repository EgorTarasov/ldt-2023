from typing import Annotated
from enum import Enum
from app.data.constants import FeedbackType
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
    feedback_type: FeedbackType,
    limit: Annotated[int, Query(..., ge=0, le=100)] = 10,
    offset: Annotated[int, Query(..., ge=0)] = 0,
    access_token: str | None = Cookie(None),
    db: Session = Depends(get_db),
) -> list[schemas.Feedback] | None:
    """
    Get feedbacks of a user
    """
    if not access_token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    db_user = await auth.get_current_user(db, access_token)
    db_feedbacks: list[models.Feedback] | None = None
    if feedback_type == "received":
        db_feedbacks = crud.get_user_received_feedbacks(db, db_user, limit, offset)
    elif feedback_type == "sent":
        db_feedbacks = crud.get_user_sent_feedbacks(db, db_user, limit, offset)
    if not db_feedbacks:
        raise HTTPException(status_code=404, detail="No feedbacks found")
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

    user = await auth.get_current_user(db, access_token)
    target = crud.get_user(db, feedback_data.target_id)
    if target is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    data = feedback_data.dict()
    data["sender_id"] = user.id
    feedback = schemas.Feedback(**data)
    db_feedback = crud.create_feedback(db, feedback)

    return schemas.Feedback.from_orm(db_feedback)


@router.delete(
    "/{feedback_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_feedback(
    feedback_id: int,
    access_token: str | None = Cookie(None),
    db: Session = Depends(get_db),
):
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authorized"
        )

    user = await auth.get_current_user(db, access_token)
    crud.delete_feedback(db, user, feedback_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
