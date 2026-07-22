from pydantic import BaseModel, ConfigDict, Field, field_validator


class ChatRequest(BaseModel):

    model_config = ConfigDict(
        extra="forbid"
    )

    character_id: str = Field(
        min_length=3,
        max_length=64,
        pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$",
    )

    message: str = Field(
        min_length=1,
        max_length=8_000,
    )

    conversation_id: str | None = None


    @field_validator("message")
    @classmethod
    def message_must_not_be_blank(
        cls,
        value: str,
    ) -> str:

        value = value.strip()

        if not value:
            raise ValueError(
                "Message cannot be blank"
            )

        return value



class AssistantMessageResponse(BaseModel):

    model_config = ConfigDict(
        extra="forbid"
    )

    id: str | int

    content: str = Field(
        min_length=1,
    )



class ChatResponse(BaseModel):

    model_config = ConfigDict(
        extra="forbid"
    )

    conversation_id: str

    character_id: str

    assistant_message: AssistantMessageResponse

    memory_summary: str = ""