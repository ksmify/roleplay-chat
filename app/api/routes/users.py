from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import httpx

from app.db.session import get_db
from app.db.models import User, Conversation, Message, Character, Follow

from app.schemas.user import (
    UserResponse,
    UsernameUpdate,
)

from app.services.user_service import (
    get_or_create_user,
    update_username,
)

from app.auth.dependencies import (
    get_current_user,
    CurrentUser,
)

# ── Google OAuth Config ────────────────────────────────────────────
GOOGLE_WEB_CLIENT_ID = "535824635473-hb4a7lu3nm8t8bhdaup8ik4ee54bnump.apps.googleusercontent.com"

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


# ── Real Google Sign-In endpoint ───────────────────────────────────
@router.post("/auth/google", response_model=UserResponse)
async def google_auth(
    id_token: str,
    db: Session = Depends(get_db),
):
    """
    Verifies a Google ID token sent from the Flutter app.
    Creates or retrieves the user and returns their data.
    """
    # Verify token with Google
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            "https://oauth2.googleapis.com/tokeninfo",
            params={"id_token": id_token},
            timeout=10.0,
        )

    if resp.status_code != 200:
        raise HTTPException(status_code=401, detail="Invalid Google token")

    token_data = resp.json()

    # Verify the token was issued for our app
    aud = token_data.get("aud", "")
    if aud not in (GOOGLE_WEB_CLIENT_ID,):
        raise HTTPException(status_code=401, detail="Token audience mismatch")

    google_id = token_data.get("sub")
    email = token_data.get("email", "")
    name = token_data.get("name") or email.split("@")[0]
    avatar_url = token_data.get("picture")

    if not google_id:
        raise HTTPException(status_code=401, detail="Missing subject in token")

    user = get_or_create_user(
        db,
        google_id=google_id,
        email=email,
        username=name,
        avatar_url=avatar_url,
    )
    return user


@router.post(
    "/login-test",
    response_model=UserResponse,
)
async def test_login(
    google_id: str,
    email: str,
    username: str,
    avatar_url: str | None = None,
    db: Session = Depends(get_db),
):
    user = get_or_create_user(
        db,
        google_id=google_id,
        email=email,
        username=username,
        avatar_url=avatar_url,
    )
    return user


@router.get("/check-username")
async def check_username_availability(
    username: str,
    current_user_id: str | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(User).filter(User.username.ilike(username.strip()))
    if current_user_id:
        query = query.filter(User.id != current_user_id)
    existing = query.first()
    return {"username": username, "is_available": existing is None}


@router.get(
    "/me",
    response_model=UserResponse,
)
async def get_my_profile(
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.id == current_user.id).first()
    if user:
        return user
    return current_user


@router.get(
    "/{user_id}",
    response_model=UserResponse,
)
async def get_user_profile(
    user_id: str,
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )
    return user


@router.put(
    "/me",
    response_model=UserResponse,
)
async def update_my_profile(
    data: UsernameUpdate,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    updated_user = update_username(
        db,
        current_user.id,
        data.username,
        description=data.description,
        avatar_url=data.avatar_url,
    )

    if updated_user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    return updated_user


@router.delete(
    "/me",
)
async def delete_my_account(
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # 1. Find user's conversations and delete their messages
    conversations = db.query(Conversation).filter(Conversation.user_id == current_user.id).all()
    for conv in conversations:
        db.query(Message).filter(Message.conversation_id == conv.id).delete(synchronize_session=False)
        db.delete(conv)

    # 2. Delete user's custom created characters
    db.query(Character).filter(Character.creator_id == current_user.id).delete(synchronize_session=False)

    # 3. Delete user
    user = db.query(User).filter(User.id == current_user.id).first()
    if user:
        db.delete(user)

    db.commit()
    return {"message": "User account and all associated data deleted successfully."}


@router.post("/{user_id}/follow")
async def follow_user(
    user_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.id == user_id:
        raise HTTPException(status_code=400, detail="Cannot follow yourself")

    existing = db.query(Follow).filter(
        Follow.follower_id == current_user.id,
        Follow.following_id == user_id,
    ).first()

    if not existing:
        follow = Follow(follower_id=current_user.id, following_id=user_id)
        db.add(follow)
        db.commit()

    return {"message": "Followed successfully", "is_following": True}


@router.post("/{user_id}/unfollow")
async def unfollow_user(
    user_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    existing = db.query(Follow).filter(
        Follow.follower_id == current_user.id,
        Follow.following_id == user_id,
    ).first()

    if existing:
        db.delete(existing)
        db.commit()

    return {"message": "Unfollowed successfully", "is_following": False}


@router.get("/{user_id}/stats")
async def get_user_stats(
    user_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    followers_count = db.query(Follow).filter(Follow.following_id == user_id).count()
    following_count = db.query(Follow).filter(Follow.follower_id == user_id).count()
    is_following = db.query(Follow).filter(
        Follow.follower_id == current_user.id,
        Follow.following_id == user_id,
    ).first() is not None

    return {
        "user_id": user_id,
        "followers_count": followers_count,
        "following_count": following_count,
        "is_following": is_following,
    }