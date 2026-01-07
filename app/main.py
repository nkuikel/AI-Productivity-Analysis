from fastapi import FastAPI

from app.routers import health
from app.routers import users
from app.routers import ingest
from app.routers import analytics
from app.db import Base, engine
from app import models  # noqa: F401

app = FastAPI()

app.include_router(health.router)
app.include_router(users.router)
app.include_router(ingest.router)
app.include_router(analytics.router)



@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)
