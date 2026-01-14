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
    expected = getattr(settings, "JOB_SECRET", None)
    if not expected:
        # Misconfiguration: secret not set in env
        raise HTTPException(status_code=500, detail="JOB_SECRET not configured")

    if not x_job_secret or not hmac.compare_digest(x_job_secret, expected):
        raise HTTPException(status_code=401, detail="Unauthorized")


@router.post("/nightly-refresh")
def nightly_refresh(
    db: Session = Depends(get_db),
    x_job_secret: str | None = Header(default=None, alias="X-Job-Secret"),
):
    """
    Nightly pipeline:
    - For each user with github_username:
      - ingest recent GitHub events
      - recompute focus sessions for last N hours
    Protected by X-Job-Secret header.
    """
    _require_job_secret(x_job_secret)

    # Choose your nightly window
    HOURS_BACK = 24
    MIN_EVENTS = 3
    LIMIT = 100  # fetch up to 100 recent events/user

    users = db.query(User).filter(User.github_username.isnot(None)).all()

    total_ingested = 0
    total_focus_created = 0
    processed_users = 0

    for u in users:
        gh = (u.github_username or "").strip()
        if not gh:
            continue

        processed_users += 1

        # 1) Ingest (idempotent now, thanks to Step 18)
        ingested = ingest_recent_github_events(
            db,
            user_id=u.id,
            github_username=gh,
            limit=LIMIT,
        )
        total_ingested += ingested

        # 2) Recompute focus (derived data)
        created = recompute_focus_sessions_last_hours(
            db,
            user_id=u.id,
            hours=HOURS_BACK,
            min_events=MIN_EVENTS,
        )
        total_focus_created += created

    return {
        "status": "ok",
        "users_processed": processed_users,
        "events_ingested": total_ingested,
        "focus_sessions_created": total_focus_created,
        "hours": HOURS_BACK,
        "min_events": MIN_EVENTS,
        "limit": LIMIT,
    }
