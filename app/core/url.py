from app.core.config import settings



def build_avatar_url(
    avatar_url: str | None,
) -> str | None:


    if avatar_url is None or avatar_url == "":
        return None


    if avatar_url.startswith(
        "http"
    ):
        return avatar_url



    return (
        settings.base_url.rstrip("/")
        +
        "/"
        +
        avatar_url.lstrip("/")
    )