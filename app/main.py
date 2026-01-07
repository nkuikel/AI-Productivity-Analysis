from fastapi import FastAPI

from app.routers import health
from app.db import Base, engine

# IMPORTANT: import models so SQLAlchemy "registers" the tables with Base.metadata
from app import models  # noqa: F401

app = FastAPI()

app.include_router(health.router)


@app.on_event("startup")
def on_startup() -> None:
    # This will connect using DATABASE_URL and create tables if they don't exist.
    Base.metadata.create_all(bind=engine)
