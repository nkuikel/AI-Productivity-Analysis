from collections.abc import Generator

from app.db import SessionLocal


def get_db() -> Generator:
    """
    FastAPI dependency that provides a database session
    per request and ensures it is closed afterwards.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
