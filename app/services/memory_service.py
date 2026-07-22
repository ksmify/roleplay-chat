from __future__ import annotations

from uuid import UUID


class MemoryService:
    """
    Placeholder memory service.

    Persistent conversation memory is handled by:
    - database Message table
    - Conversation.memory_summary
    - app.memory.store
    - app.memory.conversation

    This class exists only for compatibility with older imports.
    """

    def create_conversation(self) -> UUID:
        raise NotImplementedError(
            "Use database conversation creation instead."
        )

    def get_messages(
        self,
        conversation_id: UUID,
    ):
        raise NotImplementedError(
            "Use database message storage instead."
        )

    def append_message(
        self,
        conversation_id: UUID,
        message,
    ) -> None:
        raise NotImplementedError(
            "Use database message storage instead."
        )

    def clear_conversation(
        self,
        conversation_id: UUID,
    ) -> None:
        raise NotImplementedError(
            "Use database conversation storage instead."
        )


memory_service = MemoryService()