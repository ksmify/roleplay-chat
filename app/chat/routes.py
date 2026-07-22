from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.models import (
    Conversation,
    Message,
    Character,
)

from app.db.session import get_db

from app.auth.dependencies import (
    get_current_user,
    CurrentUser,
)

from app.schemas.chat import (
    AssistantMessageResponse,
    ChatResponse,
)

from app.chat.service import (
    create_conversation,
    create_message,
    create_ai_message,
    get_character_context,
    build_ai_prompt,
    convert_to_llm_messages,
)

from app.services.character_service import (
    get_database_character,
    get_builtin_character,
)

from app.memory.conversation import (
    build_memory_context,
)

from app.memory.store import (
    get_memory_messages,
    update_conversation_memory,
)

from app.memory.summarizer import (
    summarize_messages,
)

from app.llm.factory import get_provider

from app.llm.models import (
    LLMMessage,
    LLMRole,
)


router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)


@router.post(
    "/start/{character_id}",
)
async def start_chat(
    character_id: str,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    try:
        character = get_builtin_character(character_id)
    except Exception:
        character = get_database_character(db, character_id)

    if character is None:
        raise HTTPException(
            status_code=404,
            detail="Character not found",
        )

    conversation = create_conversation(
        db,
        user_id=current_user.id,
        character_id=character_id,
    )

    if character.greeting:
        create_ai_message(
            db,
            conversation_id=conversation.id,
            content=character.greeting,
        )

    return {
        "conversation_id": conversation.id,
        "character_id": character_id,
    }


@router.post(
    "/{conversation_id}/message",
    response_model=ChatResponse,
)
async def send_message(
    conversation_id: str,
    content: str,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    conversation = (
        db.query(Conversation)
        .filter(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id,
        )
        .first()
    )

    if conversation is None:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found",
        )

    create_message(
        db,
        conversation_id=conversation_id,
        role="user",
        content=content,
    )

    memory_context = build_memory_context(
        db,
        conversation_id,
    )

    character_context = get_character_context(
        db,
        conversation.character_id,
    )

    system_prompt = build_ai_prompt(
        character_context,
        memory_context,
    )

    messages = (
        db.query(Message)
        .filter(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
        .all()
    )

    recent_messages = messages[-20:]

    llm_messages = [
        LLMMessage(
            role=LLMRole.SYSTEM,
            content=system_prompt,
        )
    ]

    llm_messages.extend(
        convert_to_llm_messages(recent_messages)
    )

    provider = get_provider()

    # Robust dict vs object check for character_context
    if isinstance(character_context, dict):
        content_rating = character_context.get("content_rating", "safe")
    else:
        content_rating = getattr(character_context, "content_rating", "safe")

    is_nsfw = content_rating == "adult"
    dynamic_temp = 1.05 if is_nsfw else 0.90

    ai_response = await provider.generate(
        llm_messages,
        temperature=dynamic_temp,
    )

    assistant_message = create_ai_message(
        db,
        conversation_id=conversation_id,
        content=ai_response,
    )

    memory_messages = get_memory_messages(
        db,
        conversation_id,
    )

    memory_data = [
        {
            "role": message.role,
            "content": message.content,
        }
        for message in memory_messages
    ]

    summary = await summarize_messages(memory_data)

    update_conversation_memory(
        db,
        conversation_id,
        summary,
    )

    return ChatResponse(
        conversation_id=conversation_id,
        character_id=conversation.character_id,
        assistant_message=AssistantMessageResponse(
            id=str(assistant_message.id),
            content=assistant_message.content,
        ),
        memory_summary=summary,
    )


@router.get(
    "/conversations",
)
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
        character = get_database_character(
            db,
            conversation.character_id,
        )

        if character is None:
            try:
                character = get_builtin_character(conversation.character_id)
            except Exception:
                character = None

        user_message = (
            db.query(Message)
            .filter(
                Message.conversation_id == conversation.id,
                Message.role == "user",
            )
            .first()
        )
        if not user_message:
            continue

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


@router.get(
    "/{conversation_id}/messages",
)
async def get_messages(
    conversation_id: str,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    conversation = (
        db.query(Conversation)
        .filter(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id,
        )
        .first()
    )

    if conversation is None:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found",
        )

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
    Deletes a specific message by its 0-based index from DB permanently.
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

    raise HTTPException(status_code=404, detail="Message not found")


@router.delete("/messages/{message_id}")
async def delete_message_by_id(
    message_id: str,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    """
    Deletes a specific message by its unique ID directly from DB.
    """
    msg = db.query(Message).filter(Message.id == message_id).first()
    if msg:
        db.delete(msg)
        db.commit()
        return {"status": "deleted", "message_id": message_id}

    raise HTTPException(status_code=404, detail="Message not found")


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