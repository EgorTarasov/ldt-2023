from typing import Annotated
from fastapi import APIRouter, Cookie, Depends, HTTPException, status, Response, Request
from sqlalchemy.orm import Session
from app.data import crud, models, schemas


from app.utils.settings import settings
from app.utils.logging import log


router = APIRouter(prefix="/test", tags=["test"])


@router.get("/")
async def create_user(
    request: Request,
    response: Response,
):
    """
    request.client.host - получить ip адрес

    """
    log.debug(request.state.db)

    return {"status": 200}
