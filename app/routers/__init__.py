import app.routers.users as users
from fastapi import APIRouter

router = APIRouter()
router.include_router(users.router)
