import app.routers.users as users
import app.routers.feedback as feedback
import app.routers.intern_application as intern_application
import app.routers.test as test
import app.routers.vacancy as vacancy
import app.routers.mailing as mailing
from fastapi import APIRouter

router = APIRouter(prefix="/api")
router.include_router(users.router)
router.include_router(feedback.router)
router.include_router(intern_application.router)
router.include_router(test.router)
router.include_router(vacancy.router)
router.include_router(mailing.router)
