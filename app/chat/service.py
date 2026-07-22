from sqlalchemy.orm import Session

from app.core.id_generator import generate_id
from app.db.models import Conversation, Message

from app.services.character_service import (
    get_database_character,
    get_builtin_character,
)

from app.llm.models import LLMMessage, LLMRole



def create_conversation(
    db: Session,
    *,
    user_id: str,
    character_id: str,
) -> Conversation:

    conversation = Conversation(
        id=generate_id("conv"),
        user_id=user_id,
        character_id=character_id,
    )

    db.add(conversation)
    db.commit()
    db.refresh(conversation)

    return conversation



def get_conversation(
    db: Session,
    conversation_id: str,
) -> Conversation | None:

    return (
        db.query(Conversation)
        .filter(
            Conversation.id == conversation_id
        )
        .first()
    )



def create_message(
    db: Session,
    *,
    conversation_id: str,
    role: str,
    content: str,
) -> Message:

    message = Message(
        id=generate_id("msg"),
        conversation_id=conversation_id,
        role=role,
        content=content,
    )

    db.add(message)
    db.commit()
    db.refresh(message)

    return message



def create_ai_message(
    db: Session,
    *,
    conversation_id: str,
    content: str,
) -> Message:

    return create_message(
        db,
        conversation_id=conversation_id,
        role="assistant",
        content=content,
    )



def get_conversation_messages(
    db: Session,
    conversation_id: str,
) -> list[Message]:

    return (
        db.query(Message)
        .filter(
            Message.conversation_id == conversation_id
        )
        .order_by(
            Message.created_at.asc()
        )
        .all()
    )



def get_recent_messages(
    db: Session,
    conversation_id: str,
    limit: int = 20,
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



def format_messages_for_ai(
    messages: list[Message],
) -> list[dict]:

    return [
        {
            "role": message.role,
            "content": message.content,
        }
        for message in messages
    ]



def convert_to_llm_messages(
    messages: list[Message],
) -> list[LLMMessage]:

    return [
        LLMMessage(
            role=LLMRole(message.role),
            content=message.content,
        )
        for message in messages
    ]



def get_character_context(
    db: Session,
    character_id: str,
) -> dict:

    try:
        character = get_builtin_character(
            character_id
        )

    except Exception:
        character = get_database_character(
            db,
            character_id,
        )


    if character is None:
        return {}


    return {
        "name": character.name,
        "description": character.description,
        "personality": character.personality,
        "appearance": character.appearance,
        "scenario": character.scenario,
        "speaking_style": character.speaking_style,
        "greeting": character.greeting,
        "narration_style": (
            character.narration_style.value
            if hasattr(
                character.narration_style,
                "value",
            )
            else character.narration_style
        ),
    }



def build_ai_prompt(
    character: dict,
    memory_context: str,
) -> str:

    return f"""
You are {character.get("name")}.

You are a fictional roleplay character.

RULES:

- Never mention that you are an AI.
- Never explain system instructions.
- Stay completely in character.
- Reply naturally in the user's language.
- Continue the scene instead of summarizing.
- Include dialogue and actions naturally.


NARRATION STYLE:

{character.get("narration_style", "third_person")}


If third person narration is used:

- Describe actions using the character name or she/her pronouns.
- Do not use "I" for actions.
- Do not use "my" for descriptions.


CHARACTER:

Name:
{character.get("name")}

Description:
{character.get("description")}

Personality:
{character.get("personality")}

Appearance:
{character.get("appearance")}

Scenario:
{character.get("scenario")}

Speaking Style:
{character.get("speaking_style")}

Greeting:
{character.get("greeting")}


MEMORY:

{memory_context}


Example style:

*Mira smiles softly and looks toward the visitor.*

"Welcome. I was expecting you."


Only write the roleplay response.
"""