from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class Character(Base):
    __tablename__ = "characters"

    id: Mapped[str] = mapped_column(
        String(64),
        primary_key=True,
    )

    name: Mapped[str] = mapped_column(
        String(80),
        nullable=False,
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    personality: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    appearance: Mapped[str] = mapped_column(
        Text,
        default="",
    )

    scenario: Mapped[str] = mapped_column(
        Text,
        default="",
    )

    speaking_style: Mapped[str] = mapped_column(
        Text,
        default="",
    )

    narration_style: Mapped[str] = mapped_column(
        String(20),
        default="third_person",
    )

    tags: Mapped[str] = mapped_column(
        Text,
        default="",
    )

    creator_id: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
    )

    avatar_url: Mapped[str | None] = mapped_column(
        String(2048),
        nullable=True,
    )

    greeting: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    content_rating: Mapped[str] = mapped_column(
        String(20),
        default="safe",
    )

    visibility: Mapped[str] = mapped_column(
        String(20),
        default="private",
    )

    memory_enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
    )

    is_builtin: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        String(64),
        primary_key=True,
    )

    google_id: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
    )

    username: Mapped[str] = mapped_column(
        String(80),
        nullable=False,
    )

    avatar_url: Mapped[str | None] = mapped_column(
        String(2048),
        nullable=True,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )


class Conversation(Base):
    __tablename__ = "conversations"

    id: Mapped[str] = mapped_column(
        String(64),
        primary_key=True,
    )

    user_id: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )

    character_id: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )

    memory_summary: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[str] = mapped_column(
        String(64),
        primary_key=True,
    )

    conversation_id: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )

    role: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )


class Follow(Base):
    __tablename__ = "follows"

    follower_id: Mapped[str] = mapped_column(
        String(64),
        primary_key=True,
    )

    following_id: Mapped[str] = mapped_column(
        String(64),
        primary_key=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )