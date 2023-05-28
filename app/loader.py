from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


from app.data import models
from app.data.database import engine
from app.routers import router
from app.service import mailing_service


async def on_startup():
    models.Base.metadata.create_all(bind=engine)
    mailing_service.init_email_service()


def create_app():
    app = FastAPI()
    app.add_event_handler("startup", on_startup)
    # Set all CORS enabled origins
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["https://larek.itatmisis.ru", "http://localhost:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(router)
    return app
