import app.routers.users as users
import app.routers.feedback as feedback
from fastapi import APIRouter

router = APIRouter()
router.include_router(users.router)
router.include_router(feedback.router)
