from dataclasses import dataclass
from fastapi import Depends, HTTPException, Header
from sqlalchemy.orm import Session

from app.db.models import User
from app.db.session import get_db


@dataclass
class CurrentUser:
    id: str
    google_id: str
    email: str
    username: str
    avatar_url: str | None = None
    description: str | None = None


def get_current_user(
    x_user_id: str = Header(...),
    db: Session = Depends(get_db),
) -> CurrentUser:
    user = (
        db.query(User)
        .filter(User.id == x_user_id)
        .first()
    )

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="User not authenticated",
        )

    return CurrentUser(
        id=user.id,
        google_id=user.google_id,
        email=user.email,
        username=user.username,
        avatar_url=user.avatar_url,
        description=user.description,
    )