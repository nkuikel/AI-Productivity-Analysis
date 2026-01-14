from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.deps import get_db
from app.models import ActivityEvent
from app.models import FocusSession

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

@router.get("/focus")
def focus_analytics(
    user_id: int = Query(..., description="User id to compute focus analytics for"),
    start: Optional[datetime] = Query(None, description="ISO datetime, e.g. 2026-01-01T00:00:00Z"),
    end: Optional[datetime] = Query(None, description="ISO datetime, e.g. 2026-01-08T00:00:00Z"),
    db: Session = Depends(get_db),
):
    # Defaults: last 7 days if not provided
    now = datetime.now(timezone.utc)

    if end is None:
        end = now
    if start is None:
        start = end - timedelta(days=7)

    # Ensure timezone-aware (FastAPI often parses ISO as aware; this is a safety net)
    if start.tzinfo is None:
        start = start.replace(tzinfo=timezone.utc)
    if end.tzinfo is None:
        end = end.replace(tzinfo=timezone.utc)

    if end <= start:
        return {
            "status": "error",
            "detail": "end must be after start",
        }

    # Pull only sessions that overlap [start, end]
    sessions = (
        db.query(FocusSession)
        .filter(FocusSession.user_id == user_id)
        .filter(FocusSession.start_time < end)
        .filter(FocusSession.end_time > start)
        .all()
    )

    focused_minutes = 0.0

    for s in sessions:
        overlap_start = max(s.start_time, start)
        overlap_end = min(s.end_time, end)
        if overlap_end > overlap_start:
            focused_minutes += (overlap_end - overlap_start).total_seconds() / 60.0

    total_minutes = (end - start).total_seconds() / 60.0
    focused_minutes = max(0.0, min(focused_minutes, total_minutes))
    unfocused_minutes = max(0.0, total_minutes - focused_minutes)
    focus_ratio = (focused_minutes / total_minutes) if total_minutes > 0 else 0.0

    return {
        "status": "ok",
        "user_id": user_id,
        "start": start,
        "end": end,
        "focused_minutes": round(focused_minutes, 2),
        "unfocused_minutes": round(unfocused_minutes, 2),
        "focus_ratio": round(focus_ratio, 4),
    }
