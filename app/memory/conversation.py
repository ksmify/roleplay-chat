from sqlalchemy.orm import Session

from app.db.models import Conversation
from app.memory.store import get_memory_messages


def build_memory_context(
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


    context_parts = []


    if conversation.memory_summary:
        context_parts.append(
            "Long term memory summary:\n"
            + conversation.memory_summary
        )


    messages = get_memory_messages(
        db,
        conversation_id,
        limit=20,
    )


    if messages:
        recent_messages = "\n".join(
            [
                f"{message.role}: {message.content}"
                for message in messages
            ]
        )

        context_parts.append(
            "Recent conversation:\n"
            + recent_messages
        )


    return "\n\n".join(
        context_parts
    )