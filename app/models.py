from __future__ import annotations

from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    github_username: Mapped[str | None] = mapped_column(String(100), unique=True, index=True, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    activity_events: Mapped[list[ActivityEvent]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    focus_sessions: Mapped[list[FocusSession]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class ActivityEvent(Base):
    """
    Raw activity stream.
    Examples: GitHub commit/push, app usage event, website visit, task completed, etc.
    """
    __tablename__ = "activity_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)

    event_type: Mapped[str] = mapped_column(String(100), nullable=False)  # e.g. "github_commit"
    source: Mapped[str] = mapped_column(String(100), nullable=False)      # e.g. "github"
    occurred_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Keep payload flexible early (JSON later). For now, store as text.
    metadata_json: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user: Mapped[User] = relationship(back_populates="activity_events")


class FocusSession(Base):
    """
    Higher-level session built from events.
    Later you can calculate duration, focus score, distractions, etc.
    """
    __tablename__ = "focus_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)

    started_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    ended_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)

    # Placeholder metric fields (can evolve later)
    focus_score: Mapped[int | None] = mapped_column(Integer, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user: Mapped[User] = relationship(back_populates="focus_sessions")
