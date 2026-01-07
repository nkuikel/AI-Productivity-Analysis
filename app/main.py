from fastapi import FastAPI

from app.routers import health
from app.routers import users
from app.db import Base, engine
from app import models  # noqa: F401

app = FastAPI()

app.include_router(health.router)
app.include_router(users.router)


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)
