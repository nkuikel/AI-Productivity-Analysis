from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.deps import get_db
from app.models import ActivityEvent

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/summary")
def analytics_summary(
    user_id: int = Query(..., description="User ID"),
    start: Optional[datetime] = Query(None, description="Start datetime (ISO format)"),
    end: Optional[datetime] = Query(None, description="End datetime (ISO format)"),
    db: Session = Depends(get_db),
):
    q = db.query(ActivityEvent).filter(ActivityEvent.user_id == user_id)

    if start is not None:
        q = q.filter(ActivityEvent.occurred_at >= start)
    if end is not None:
        q = q.filter(ActivityEvent.occurred_at <= end)

    total_events = q.count()

    rows = (
        db.query(ActivityEvent.event_type, func.count(ActivityEvent.id))
        .filter(ActivityEvent.user_id == user_id)
        .filter(ActivityEvent.occurred_at >= start if start is not None else True)
        .filter(ActivityEvent.occurred_at <= end if end is not None else True)
        .group_by(ActivityEvent.event_type)
        .order_by(func.count(ActivityEvent.id).desc())
        .all()
    )

    events_by_type = {event_type: count for event_type, count in rows}

    return {
        "user_id": user_id,
        "start": start,
        "end": end,
        "total_events": total_events,
        "events_by_type": events_by_type,
    }
