from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.models import (
    Message,
    Conversation,
    Character,
)

from app.db.session import get_db
from app.auth.dependencies import (
    get_current_user,
    CurrentUser,
)


router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)


@router.get("/conversations")
async def get_conversations(
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    conversations = (
        db.query(Conversation)
        .filter(Conversation.user_id == current_user.id)
        .order_by(Conversation.updated_at.desc())
        .all()
    )

    result = []

    for conversation in conversations:
        character = (
            db.query(Character)
            .filter(Character.id == conversation.character_id)
            .first()
        )

        last_message = (
            db.query(Message)
            .filter(Message.conversation_id == conversation.id)
            .order_by(Message.created_at.desc())
            .first()
        )

        result.append(
            {
                "conversation_id": conversation.id,
                "character_id": conversation.character_id,
                "character_name": character.name if character else "Unknown",
                "avatar_url": character.avatar_url if character else None,
                "last_message": last_message.content if last_message else "",
                "updated_at": conversation.updated_at,
            }
        )

    return result


@router.get("/{conversation_id}/messages")
async def get_messages(
    conversation_id: str,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    messages = (
        db.query(Message)
        .filter(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
        .all()
    )

    return [
        {
            "id": message.id,
            "role": message.role,
            "content": message.content,
            "created_at": message.created_at,
        }
        for message in messages
    ]


@router.delete("/{conversation_id}/messages/{message_index}")
async def delete_message_by_index(
    conversation_id: str,
    message_index: int,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    """
    Deletes a specific message by its index (0-based) directly from Database and Memory.
    """
    messages = (
        db.query(Message)
        .filter(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
        .all()
    )

    if 0 <= message_index < len(messages):
        target_msg = messages[message_index]
        db.delete(target_msg)
        db.commit()
        return {"status": "deleted", "message_id": target_msg.id}

    return {"status": "not_found"}


@router.delete("/messages/{message_id}")
async def delete_message_by_id(
    message_id: str,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    """
    Deletes a specific message by its unique ID.
    """
    msg = db.query(Message).filter(Message.id == message_id).first()
    if msg:
        db.delete(msg)
        db.commit()
        return {"status": "deleted", "message_id": message_id}

    return {"status": "not_found"}


@router.delete("/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    """
    Deletes an entire conversation and all its messages.
    """
    conv = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    if conv.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    db.query(Message).filter(Message.conversation_id == conversation_id).delete()
    db.delete(conv)
    db.commit()
    return {"status": "deleted", "conversation_id": conversation_id}