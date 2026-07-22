from __future__ import annotations
import re

from openai import AsyncOpenAI

from app.core.config import settings
from app.llm.models import LLMMessage
from app.llm.provider import LLMProvider


def ensure_complete_sentence(text: str) -> str:
    """
    If text was truncated mid-sentence or mid-word (e.g. 'Vermeil\''),
    trim back to the last valid completed sentence (. ! ?) and ensure quotes (") and asterisks (*) are properly closed.
    """
    text = text.strip()
    if not text:
        return text

    # Find the last valid sentence ending (. ! ?)
    last_punct = max(text.rfind('.'), text.rfind('!'), text.rfind('?'))
    if last_punct != -1 and last_punct >= 20 and last_punct < len(text) - 1:
        # Check if what's after last_punct is an incomplete fragment
        after = text[last_punct + 1:].strip()
        if not after.endswith(('.', '!', '?', '"', '*')):
            text = text[:last_punct + 1].strip()

    # Guarantee final punctuation if missing
    if text and text[-1] not in '.!?*"\'' and not text.endswith('...'):
        text += '.'

    # Balance unclosed quotes (")
    quote_count = text.count('"')
    if quote_count % 2 != 0:
        text += '"'

    # Balance unclosed asterisks (*)
    asterisk_count = text.count('*')
    if asterisk_count % 2 != 0:
        text += '*'

    return text


class OpenRouterProvider(LLMProvider):
    """
    OpenRouter implementation of the LLM provider with 256 max token generation limit.
    """

    def __init__(self) -> None:
        self._client = AsyncOpenAI(
            api_key=settings.openrouter_api_key,
            base_url="https://openrouter.ai/api/v1",
            timeout=60.0,
            default_headers={
                "HTTP-Referer": "https://an-ai.app",
                "X-Title": "An AI",
            },
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
        temperature: float = 1.15,
    ) -> str:
        """
        Generates a roleplay response with 256 token limit.
        """
        print("MODEL:", settings.openrouter_model)

        response = await self._client.chat.completions.create(
            model=settings.openrouter_model,
            messages=self._build_messages(messages),
            temperature=temperature,
            max_tokens=256,
        )

        if not response.choices:
            raise RuntimeError("OpenRouter returned no choices.")

        reply = response.choices[0].message.content

        if not reply:
            raise RuntimeError("OpenRouter returned an empty response.")

        # Guarantee complete sentence, balanced quotes and asterisks
        return ensure_complete_sentence(reply)