from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import UniqueConstraint

from app.db import Base


def utc_now() -> datetime:
    """Timezone-aware UTC 'now' for consistent timestamps across Postgres/Neon."""
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    username: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        index=True,
        nullable=False,
    )

    # Keep unique=True if you want a 1:1 mapping between app user and GitHub username.
    github_username: Mapped[str | None] = mapped_column(
        String(100),
        unique=True,
        index=True,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )

    # Relationships
    activity_events: Mapped[list["ActivityEvent"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    focus_sessions: Mapped[list["FocusSession"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )


class ActivityEvent(Base):
    """
    Raw activity stream.
    Examples: GitHub push, PR, issue, app usage event, website visit, etc.
    """
    __table_args__ = (
    UniqueConstraint("source", "external_id", name="uq_activity_events_source_external_id"),
)


    __tablename__ = "activity_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    # e.g. "PushEvent", "PullRequestEvent", etc.
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)

    # e.g. "github"
    source: Mapped[str] = mapped_column(String(100), nullable=False)

    external_id = Column(String, nullable=False)

    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
        index=True,
    )

    # Keep payload flexible early (JSON later). For now, store as text.
    metadata_json: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )

    # Relationships
    user: Mapped["User"] = relationship(back_populates="activity_events")


class FocusSession(Base):
    __tablename__ = "focus_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    start_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
    )
    end_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    event_count: Mapped[int] = mapped_column(Integer, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )

    user: Mapped["User"] = relationship(back_populates="focus_sessions")
