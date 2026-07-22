from sqlalchemy.orm import Session

from app.core.id_generator import generate_id
from app.db.models import User


def get_user_by_google_id(
    db: Session,
    google_id: str,
) -> User | None:
    return (
        db.query(User)
        .filter(User.google_id == google_id)
        .first()
    )


def create_user(
    db: Session,
    *,
    google_id: str,
    email: str,
    username: str,
    avatar_url: str | None = None,
    description: str | None = None,
) -> User:
    user = User(
        id=generate_id("u"),
        google_id=google_id,
        email=email,
        username=username,
        avatar_url=avatar_url,
        description=description,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def get_or_create_user(
    db: Session,
    *,
    google_id: str,
    email: str,
    username: str,
    avatar_url: str | None = None,
    description: str | None = None,
) -> User:
    existing_user = get_user_by_google_id(
        db,
        google_id,
    )

    if existing_user:
        setattr(existing_user, "is_new_user", False)
        return existing_user

    new_user = create_user(
        db,
        google_id=google_id,
        email=email,
        username=username,
        avatar_url=avatar_url,
        description=description,
    )
    setattr(new_user, "is_new_user", True)
    return new_user


def update_username(
    db: Session,
    user_id: str,
    username: str,
    description: str | None = None,
    avatar_url: str | None = None,
) -> User | None:
    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if user is None:
        return None

    user.username = username
    if description is not None:
        user.description = description
    if avatar_url == "":
        user.avatar_url = None
    elif avatar_url is not None:
        user.avatar_url = avatar_url

    db.commit()
    db.refresh(user)

    return user