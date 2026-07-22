from sqlalchemy.orm import Session

from app.db.models import Message, Conversation


def get_memory_messages(
    db: Session,
    conversation_id: str,
    limit: int = 50,
) -> list[Message]:

    return (
        db.query(Message)
        .filter(
            Message.conversation_id == conversation_id
        )
        .order_by(
            Message.created_at.desc()
        )
        .limit(limit)
        .all()[::-1]
    )


def get_conversation_memory(
    db: Session,
    conversation_id: str,
) -> str:

    conversation = (
        db.query(Conversation)
        .filter(
            Conversation.id == conversation_id
        )
        .first()
    )

    if conversation is None:
        return ""

    return conversation.memory_summary or ""


def update_conversation_memory(
    db: Session,
    conversation_id: str,
    summary: str,
) -> Conversation | None:

    conversation = (
        db.query(Conversation)
        .filter(
            Conversation.id == conversation_id
        )
        .first()
    )

    if conversation is None:
        return None

    conversation.memory_summary = summary

    db.commit()
    db.refresh(conversation)

    return conversation