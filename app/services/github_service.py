from __future__ import annotations

import json
from datetime import datetime
from typing import Any

import requests
from sqlalchemy.orm import Session

from app.config import settings
from app.models import ActivityEvent


def _parse_github_datetime(dt: str | None) -> datetime:
    # GitHub gives ISO timestamps like "2026-01-07T17:24:39Z"
    if not dt:
        return datetime.utcnow()
    return datetime.fromisoformat(dt.replace("Z", "+00:00"))


def ingest_recent_github_events(
    db: Session,
    *,
    user_id: int,
    github_username: str,
    limit: int = 30,
) -> int:
    """
    Fetch recent public GitHub events for a username and store them as ActivityEvent rows.
    Returns number of inserted rows.
    """
    url = f"https://api.github.com/users/{github_username}/events/public"
    headers: dict[str, str] = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "ai-productivity-analysis",
    }

    # Optional auth (recommended to avoid rate limits)
    if settings.GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {settings.GITHUB_TOKEN}"

    resp = requests.get(url, headers=headers, timeout=20)

    # Helpful error messages
    if resp.status_code == 404:
        raise ValueError(f"GitHub user '{github_username}' not found")
    resp.raise_for_status()

    events: list[dict[str, Any]] = resp.json()
    events = events[:limit]

    inserted = 0
    for e in events:
        activity = ActivityEvent(
            user_id=user_id,
            event_type=e.get("type", "unknown"),
            source="github",
            occurred_at=_parse_github_datetime(e.get("created_at")),
            metadata_json=json.dumps(e),
        )
        db.add(activity)
        inserted += 1

    db.commit()
    return inserted
