from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class LLMRole(StrEnum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


class LLMMessage(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    role: LLMRole
    content: str = Field(
        min_length=1,
    )