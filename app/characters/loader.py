from pathlib import Path

import yaml

from app.schemas.character import CharacterDefinition

BUILTIN_DEFINITIONS_DIRECTORY = Path(__file__).parent / "definitions"


def load_character_file(file_path: Path) -> CharacterDefinition:
    with file_path.open("r", encoding="utf-8") as character_file:
        raw_character = yaml.safe_load(character_file)

    if not isinstance(raw_character, dict):
        raise ValueError(
            f"Character file must contain a YAML object: {file_path}"
        )

    character = CharacterDefinition.model_validate(raw_character)

    character.is_builtin = True

    return character


def load_builtin_characters(
    definitions_directory: Path = BUILTIN_DEFINITIONS_DIRECTORY,
) -> dict[str, CharacterDefinition]:
    if not definitions_directory.is_dir():
        raise FileNotFoundError(
            f"Built-in character directory was not found: {definitions_directory}"
        )

    characters: dict[str, CharacterDefinition] = {}

    for file_path in sorted(definitions_directory.glob("*.yaml")):
        character = load_character_file(file_path)

        if character.id in characters:
            raise ValueError(
                f"Duplicate character id: {character.id}"
            )

        characters[character.id] = character

        print(
            f"Loaded: {character.id} ({character.content_rating})"
        )

    print("Characters:", list(characters.keys()))

    return characters   