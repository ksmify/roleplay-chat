import secrets


def generate_id(
    prefix: str = "",
) -> str:
    random_part = secrets.token_urlsafe(24)

    if prefix:
        return f"{prefix}_{random_part}"

    return random_part