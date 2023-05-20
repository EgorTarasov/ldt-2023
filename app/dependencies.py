from app.data.database import SessionLocal


def get_db():
    db = SessionLocal()
    with SessionLocal() as db:
        yield db
