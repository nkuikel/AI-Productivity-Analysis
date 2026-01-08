from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.models import ActivityEvent, FocusSession


def _floor_to_30_min(dt: datetime) -> datetime:
    # Keep timezone info if present
    minute_bucket = (dt.minute // 30) * 30
    return dt.replace(minute=minute_bucket, second=0, microsecond=0)


def recompute_focus_sessions_last_hours(
    db: Session,
    *,
    user_id: int,
    hours: int = 24,
    min_events: int = 3,
) -> int:
    """
    Rule:
    - Split time into 30-min windows
    - If a window has >= min_events activity events -> focused
    - Store focused windows in focus_sessions
    Returns: number of focus sessions created
    """
    now = datetime.now(timezone.utc)
    since = now - timedelta(hours=hours)

    # Load events in range
    events = (
        db.query(ActivityEvent)
        .filter(ActivityEvent.user_id == user_id)
        .filter(ActivityEvent.occurred_at >= since)
        .order_by(ActivityEvent.occurred_at.asc())
        .all()
    )

    # Bucket counts by 30-min window
    buckets: dict[datetime, int] = defaultdict(int)
    for e in events:
        dt = e.occurred_at
        # If DB returns naive datetimes, force UTC (not ideal, but prevents crashes)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)

        window_start = _floor_to_30_min(dt)
        buckets[window_start] += 1

    # Clear existing focus sessions in same range (avoid duplicates)
    db.query(FocusSession).filter(FocusSession.user_id == user_id).filter(
        FocusSession.start_time >= since
    ).delete(synchronize_session=False)

    created = 0
    for window_start, count in sorted(buckets.items()):
        if count >= min_events:
            window_end = window_start + timedelta(minutes=30)
            fs = FocusSession(
                user_id=user_id,
                start_time=window_start,
                end_time=window_end,
                event_count=count,
            )
            db.add(fs)
            created += 1

    db.commit()
    return created
