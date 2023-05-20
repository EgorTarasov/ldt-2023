from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


from app.data import models
from app.data.database import engine
from app.routers import router


async def on_startup():
    models.Base.metadata.create_all(bind=engine)


def create_app():
    app = FastAPI()
    app.add_event_handler("startup", on_startup)
    # Set all CORS enabled origins
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(router)
    return app
