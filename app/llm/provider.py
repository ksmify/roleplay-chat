from __future__ import annotations

from abc import ABC, abstractmethod

from app.llm.models import LLMMessage


class LLMProvider(ABC):
    """
    Base interface for every language model provider.

    Every provider (OpenAI, Ollama, vLLM, An AI, etc.)
    must implement this interface so the rest of the
    application never depends on a specific vendor.
    """

    @abstractmethod
    async def generate(
        self,
        messages: list[LLMMessage],
    ) -> str:
        """
        Generate a response from the language model.

        Args:
            messages:
                Ordered conversation history.

        Returns:
            Assistant response as plain text.
        """
        raise NotImplementedError