from __future__ import annotations

from app.core.config import settings
from app.llm.provider import LLMProvider


def get_provider() -> LLMProvider:
    """
    Returns the configured LLM provider.
    """

    provider = settings.llm_provider.lower()

    if provider == "local":
        from app.llm.local import LocalProvider

        return LocalProvider()

    raise ValueError(
        f"Unknown LLM provider: {provider}"
    )