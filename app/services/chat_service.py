from __future__ import annotations

from uuid import UUID

from app.llm.factory import get_provider
from app.llm.models import LLMMessage, LLMRole
from app.llm.prompts import build_character_system_prompt
from app.schemas.chat import ChatResponse
from app.services.character_service import get_builtin_character
from app.services.memory_service import memory_service


class ChatService:
    """
    Coordinates the complete roleplay pipeline.
    """

    def __init__(self) -> None:
        self._provider = get_provider()

    async def send_message(
        self,
        *,
        character_id: str,
        user_message: str,
        conversation_id: UUID | None,
    ) -> ChatResponse:

        character = get_builtin_character(
    character_id,
    allow_adult_content=True,
)
        if conversation_id is None:
            conversation_id = memory_service.create_conversation()

        history = memory_service.get_messages(
            conversation_id
        )

        system_prompt = build_character_system_prompt(
            character
        )

        messages = [
            LLMMessage(
                role=LLMRole.SYSTEM,
                content=system_prompt,
            ),
            *history,
            LLMMessage(
                role=LLMRole.USER,
                content=user_message,
            ),
        ]

        reply = await self._provider.generate(
            messages
        )

        memory_service.append_message(
            conversation_id,
            LLMMessage(
                role=LLMRole.USER,
                content=user_message,
            ),
        )

        memory_service.append_message(
            conversation_id,
            LLMMessage(
                role=LLMRole.ASSISTANT,
                content=reply,
            ),
        )

        return ChatResponse(
            conversation_id=conversation_id,
            character_id=character.id,
            reply=reply,
        )


chat_service = ChatService()