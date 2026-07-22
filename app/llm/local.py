from __future__ import annotations
import re

from openai import AsyncOpenAI

from app.core.config import settings
from app.llm.models import LLMMessage
from app.llm.provider import LLMProvider
from app.llm.openrouter import ensure_complete_sentence


class LocalProvider(LLMProvider):
    """
    Local llama.cpp provider tuned for Realistic Erotic Romance & High-End Roleplay.
    """

    def __init__(self) -> None:
        self._client = AsyncOpenAI(
            api_key="local",
            base_url=f"{settings.local_api_url}/v1",
            timeout=300.0,
        )

    @staticmethod
    def _build_messages(
        messages: list[LLMMessage],
    ) -> list[dict[str, str]]:

        return [
            {
                "role": message.role.value,
                "content": message.content,
            }
            for message in messages
        ]

    async def generate(
        self,
        messages: list[LLMMessage],
        temperature: float = 1.05,
    ) -> str:

        print("=== LOCAL PROVIDER (REALISTIC ROMANCE TONE) ===")
        print("Temperature:", temperature)
        print("Max tokens: 256")
        print("Message count:", len(messages))

        # Precision parameters for serious, uncensored, realistic intimacy
        response = await self._client.chat.completions.create(
            model="local-model",
            messages=self._build_messages(messages),
            temperature=temperature,
            top_p=0.92,
            presence_penalty=0.25,
            frequency_penalty=0.25,
            max_tokens=256,
            extra_body={
                "min_p": 0.05,
            },
        )

        if not response.choices:
            raise RuntimeError("Local model returned no choices.")

        choice = response.choices[0]

        print("\n========== PERFORMANCE ==========")
        if response.usage:
            print(f"Prompt tokens      : {response.usage.prompt_tokens}")
            print(f"Completion tokens  : {response.usage.completion_tokens}")
            print(f"Total tokens       : {response.usage.total_tokens}")

        timings = getattr(response, "timings", None)
        if timings:
            print(f"Prompt speed       : {timings.get('prompt_per_second', 0):.2f} tok/s")
            print(f"Generation speed   : {timings.get('predicted_per_second', 0):.2f} tok/s")

        print(f"Finish reason      : {choice.finish_reason}")
        print("=================================\n")

        message = choice.message
        reply = message.content

        if not reply:
            reply = getattr(message, "reasoning_content", None)

        if not reply:
            raise RuntimeError("Local model returned an empty response.")

        # Ensure complete sentence without truncation up to 256 tokens
        return ensure_complete_sentence(reply)