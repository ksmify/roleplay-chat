from enum import StrEnum
from pydantic import BaseModel, ConfigDict, Field


class CharacterVisibility(StrEnum):
    PRIVATE = "private"
    UNLISTED = "unlisted"
    PUBLIC = "public"


class ContentRating(StrEnum):
    SAFE = "safe"
    ADULT = "adult"


class NarrationStyle(StrEnum):
    FIRST_PERSON = "first_person"
    THIRD_PERSON = "third_person"


class ExampleDialogue(BaseModel):
    model_config = ConfigDict(extra="forbid")

    user: str = Field(min_length=1, max_length=2_000)
    character: str = Field(min_length=1, max_length=2_000)


class CharacterCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=80)
    description: str = Field(min_length=1, max_length=1_000)
    personality: str = Field(min_length=1, max_length=3_000)
    appearance: str = Field(default="", max_length=3_000)
    avatar_url: str | None = Field(default=None, max_length=2_048)
    scenario: str = Field(default="", max_length=3_000)
    greeting: str = Field(min_length=1, max_length=2_000)
    speaking_style: str = Field(default="", max_length=1_000)
    narration_style: NarrationStyle = NarrationStyle.THIRD_PERSON
    memory_enabled: bool = True
    example_dialogues: list[ExampleDialogue] = Field(default_factory=list, max_length=10)
    tags: list[str] = Field(default_factory=list, max_length=10)
    visibility: CharacterVisibility = CharacterVisibility.PRIVATE
    content_rating: ContentRating = ContentRating.SAFE


class CharacterDefinition(CharacterCreate):
    id: str = Field(
        min_length=3,
        max_length=32,
        pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$",
    )
    is_builtin: bool = False
    creator_id: str | None = None
    creator_username: str = "System"
    created_at: str | None = None
    message_count: int = 0


class CharacterListItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    name: str
    description: str
    avatar_url: str | None = None
    tags: list[str] = Field(default_factory=list)
    visibility: CharacterVisibility
    content_rating: ContentRating
    creator_id: str | None = None
    creator_username: str = "System"
    created_at: str | None = None
    message_count: int = 0
    greeting: str = ""
    personality: str = ""
    scenario: str = ""
    appearance: str = ""
    is_builtin: bool = False