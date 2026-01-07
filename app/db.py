from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import settings

engine = create_engine(
    settings.DATABASE_URL or "sqlite:///./local.db",
    future=True,
    pool_pre_ping=True,      # ✅ checks connection before using it
    pool_recycle=300,        # ✅ recycle connections every 5 minutes
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
