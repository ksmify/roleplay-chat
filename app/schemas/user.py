from pydantic import BaseModel, ConfigDict, Field


class UserResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str
    google_id: str
    email: str
    username: str = Field(min_length=1, max_length=80)
    avatar_url: str | None = None
    description: str | None = None
    is_new_user: bool = False


class UserProfileUpdate(BaseModel):
    model_config = ConfigDict(extra="ignore")

    username: str | None = Field(default=None, min_length=1, max_length=80)
    avatar_url: str | None = None
    description: str | None = None


class UsernameUpdate(BaseModel):
    model_config = ConfigDict(extra="ignore")

    username: str = Field(min_length=1, max_length=80)
    description: str | None = None
    avatar_url: str | None = None