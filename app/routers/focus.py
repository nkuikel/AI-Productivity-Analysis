from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.deps import get_db
from app.models import User
from app.services.focus_rules import recompute_focus_sessions_last_hours

router = APIRouter(prefix="/focus", tags=["focus"])


@router.post("/recompute/{user_id}")
def recompute_focus(
    user_id: int,
    hours: int = Query(24, ge=1, le=168, description="How many hours back to recompute"),
    min_events: int = Query(3, ge=1, le=50, description="Events needed in a 30-min window to be focused"),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    n = recompute_focus_sessions_last_hours(db, user_id=user_id, hours=hours, min_events=min_events)
    return {"status": "ok", "user_id": user_id, "hours": hours, "min_events": min_events, "focus_sessions_created": n}
