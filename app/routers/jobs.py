from __future__ import annotations

import hmac
from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.config import settings
from app.deps import get_db
from app.models import User
from app.services.github_service import ingest_recent_github_events
from app.services.focus_rules import recompute_focus_sessions_last_hours

router = APIRouter(prefix="/jobs", tags=["jobs"])


def _require_job_secret(x_job_secret: str | None) -> None:
    expected = settings.JOB_SECRET
    if not expected:
        raise HTTPException(status_code=500, detail="JOB_SECRET not configured")

    if not x_job_secret or not hmac.compare_digest(x_job_secret, expected):
        raise HTTPException(status_code=401, detail="Unauthorized")


@router.post("/nightly-refresh")
def nightly_refresh(
    db: Session = Depends(get_db),
    x_job_secret: str | None = Header(default=None, alias="X-Job-Secret"),
):
    _require_job_secret(x_job_secret)

    HOURS_BACK = 24
    MIN_EVENTS = 3
    LIMIT = 100

    users = db.query(User).filter(User.github_username.isnot(None)).all()

    users_processed = 0
    total_events_ingested = 0
    total_focus_sessions_created = 0

    for u in users:
        gh = (u.github_username or "").strip()
        if not gh:
            continue

        users_processed += 1

        ingested = ingest_recent_github_events(
            db,
            user_id=u.id,
            github_username=gh,
            limit=LIMIT,
        )
        total_events_ingested += ingested

        created = recompute_focus_sessions_last_hours(
            db,
            user_id=u.id,
            hours=HOURS_BACK,
            min_events=MIN_EVENTS,
        )
        total_focus_sessions_created += created

    return {
        "status": "ok",
        "users_processed": users_processed,
        "total_events_ingested": total_events_ingested,
        "total_focus_sessions_created": total_focus_sessions_created,
        "hours": HOURS_BACK,
        "min_events": MIN_EVENTS,
        "limit": LIMIT,
    }
