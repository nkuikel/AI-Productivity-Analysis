from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import settings

# Create the SQLAlchemy engine using the DATABASE_URL from environment/config.
# This does not actually connect until you try to use the engine (lazy).
engine = create_engine(
    settings.DATABASE_URL or "sqlite:///./local.db",
    future=True,
)

# Session factory. Later you'll use SessionLocal() to get a session in a request.
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# Base class for your ORM models (tables will inherit from this).
Base = declarative_base()
