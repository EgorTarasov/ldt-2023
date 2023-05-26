from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from app.utils.settings import settings
from app.utils.serializer import _custom_json_serializer

engine = create_engine(
    str(settings.DATABASE_URI),
    json_serializer=_custom_json_serializer,  # , connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autoflush=True, bind=engine)

Base = declarative_base()
