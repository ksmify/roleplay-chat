from __future__ import annotations

from app.llm.factory import get_provider
from app.llm.models import LLMMessage, LLMRole



async def summarize_messages(
    messages: list[dict],
) -> str:

    if not messages:
        return ""


    conversation_text = "\n".join(
        [
            f"{message['role']}: {message['content']}"
            for message in messages
        ]
    )


    prompt = f"""
Create a long-term memory summary for this conversation.

The memory belongs ONLY to the USER.

Your job is to extract stable facts that are useful in future conversations.

ONLY save information that the user explicitly said.

Keep:

- user's name ONLY if the user directly introduced their name
- user's preferences
- user's hobbies and interests
- user's personality traits if clearly shown or stated
- important personal facts directly shared by the user
- user's goals and ongoing projects
- stable relationship preferences (for example: preferred conversation style)

STRICT RULES:

- Never guess user information.
- Never infer a name.
- Never create facts that are not directly stated.
- If a fact is unknown, omit it.

DO NOT store:

- character appearance
- character personality
- character background
- fictional locations
- roleplay scenes
- temporary actions
- greetings
- assistant messages
- what the character said or did
- events that only happened inside the fictional scenario

A good memory answers:

"What should the AI remember about this user in a future conversation?"

GOOD examples:

User likes discussing technology.
User is interested in AI development.
User enjoys creative roleplay conversations.

BAD examples:

User name: Kâsım. (unless the user explicitly said this)
User visited Marin's studio.
Marin has blonde hair.
Marin smiled at the user.
The user is in a cosplay room.

Conversation:

{conversation_text}


Return only short factual memory notes.
"""


    provider = get_provider()


    summary = await provider.generate(
        [
            LLMMessage(
                role=LLMRole.SYSTEM,
                content=(
                    "You create accurate user-only "
                    "long-term memory. Never invent facts."
                ),
            ),
            LLMMessage(
                role=LLMRole.USER,
                content=prompt,
            ),
        ]
    )


    return summary