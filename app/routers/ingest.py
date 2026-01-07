from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.deps import get_db
from app.models import User
from app.services.github_service import ingest_recent_github_events

router = APIRouter(prefix="/ingest", tags=["ingest"])


@router.post("/github/{user_id}")
def ingest_github(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not user.github_username:
        raise HTTPException(status_code=400, detail="User has no github_username")

    try:
        n = ingest_recent_github_events(db, user_id=user.id, github_username=user.github_username)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {e}")

    return {"status": "ok", "ingested": n}
