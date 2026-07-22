from sqlalchemy.orm import Session

from app.db.models import Character
from app.characters.loader import load_builtin_characters
from app.schemas.character import (
    CharacterDefinition,
    ContentRating,
)


class CharacterNotFoundError(LookupError):
    pass



def list_builtin_characters(
    *,
    allow_adult_content: bool = True,
) -> list[CharacterDefinition]:

    characters = load_builtin_characters().values()

    return [
        character
        for character in characters
        if allow_adult_content
        or character.content_rating != ContentRating.ADULT
    ]



def get_builtin_character(
    character_id: str,
    *,
    allow_adult_content: bool = True,
) -> CharacterDefinition:

    available = list_builtin_characters(
        allow_adult_content=allow_adult_content
    )

    characters = {
        character.id: character
        for character in available
    }

    try:
        return characters[character_id]

    except KeyError as error:
        raise CharacterNotFoundError(
            f"Character not found: {character_id}"
        ) from error



def create_database_character(
    db: Session,
    character: CharacterDefinition,
    creator_id: str,
) -> Character:

    db_character = Character(
        id=character.id,
        name=character.name,
        description=character.description,
        personality=character.personality,
        appearance=character.appearance,
        avatar_url=character.avatar_url,
        scenario=character.scenario,
        greeting=character.greeting,
        speaking_style=character.speaking_style,
        narration_style=character.narration_style.value,
        content_rating=character.content_rating.value,
        visibility=character.visibility.value,
        memory_enabled=character.memory_enabled,
        is_builtin=False,
        creator_id=creator_id,
        tags=",".join(character.tags),
    )

    db.add(db_character)
    db.commit()
    db.refresh(db_character)

    return db_character



def list_database_characters(
    db: Session,
) -> list[Character]:

    return db.query(Character).all()



def get_database_character(
    db: Session,
    character_id: str,
) -> Character | None:

    return (
        db.query(Character)
        .filter(
            Character.id == character_id
        )
        .first()
    )



def update_database_character(
    db: Session,
    character_id: str,
    character_data: CharacterDefinition,
) -> Character | None:

    character = (
        db.query(Character)
        .filter(
            Character.id == character_id
        )
        .first()
    )

    if character is None:
        return None


    character.name = character_data.name
    character.description = character_data.description
    character.personality = character_data.personality
    character.appearance = character_data.appearance
    character.avatar_url = character_data.avatar_url
    character.scenario = character_data.scenario
    character.greeting = character_data.greeting
    character.speaking_style = character_data.speaking_style
    character.narration_style = (
        character_data.narration_style.value
    )
    character.content_rating = (
        character_data.content_rating.value
    )
    character.visibility = (
        character_data.visibility.value
    )
    character.memory_enabled = (
        character_data.memory_enabled
    )
    character.tags = ",".join(
        character_data.tags
    )


    db.commit()
    db.refresh(character)

    return character



def delete_database_character(
    db: Session,
    character_id: str,
) -> bool:

    character = (
        db.query(Character)
        .filter(
            Character.id == character_id
        )
        .first()
    )

    if character is None:
        return False


    if character.is_builtin:
        return False


    db.delete(character)
    db.commit()

    return True