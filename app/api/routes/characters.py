from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth.dependencies import (
    get_current_user,
    CurrentUser,
)

from app.db.session import get_db
from app.db.models import Conversation, Message, User

from app.schemas.character import (
    CharacterDefinition,
    CharacterListItem,
)

from app.services.character_service import (
    list_builtin_characters,
    list_database_characters,
    create_database_character,
    get_builtin_character,
    get_database_character,
    update_database_character,
    delete_database_character,
    CharacterNotFoundError,
)

router = APIRouter(
    prefix="/characters",
    tags=["Characters"],
)


def get_character_message_count(db: Session, character_id: str) -> int:
    conv_ids = [
        c.id for c in db.query(Conversation.id).filter(Conversation.character_id == character_id).all()
    ]
    if not conv_ids:
        return 0
    return db.query(Message).filter(Message.conversation_id.in_(conv_ids)).count()


def get_creator_username(db: Session, creator_id: str | None) -> str:
    if not creator_id:
        return "System"
    user = db.query(User).filter(User.id == creator_id).first()
    return user.username if user else "System"


def database_character_to_definition(
    character,
    db: Session,
) -> CharacterDefinition:
    msg_count = get_character_message_count(db, character.id)
    creator_uname = get_creator_username(db, character.creator_id)
    created_str = character.created_at.strftime("%Y-%m-%d") if character.created_at else None

    return CharacterDefinition(
        id=character.id,
        name=character.name,
        description=character.description,
        personality=character.personality,
        appearance=character.appearance,
        avatar_url=character.avatar_url,
        scenario=character.scenario,
        greeting=character.greeting,
        speaking_style=character.speaking_style,
        narration_style=character.narration_style,
        memory_enabled=character.memory_enabled,
        example_dialogues=[],
        tags=(
            character.tags.split(",")
            if character.tags
            else []
        ),
        visibility=character.visibility,
        content_rating=character.content_rating,
        creator_id=character.creator_id,
        creator_username=creator_uname,
        created_at=created_str,
        is_builtin=character.is_builtin,
        message_count=msg_count,
    )


def database_character_to_list_item(
    character,
    db: Session,
) -> CharacterListItem:
    msg_count = get_character_message_count(db, character.id)
    creator_uname = get_creator_username(db, character.creator_id)
    created_str = character.created_at.strftime("%Y-%m-%d") if character.created_at else None

    return CharacterListItem(
        id=character.id,
        name=character.name,
        description=character.description,
        avatar_url=character.avatar_url,
        tags=(
            character.tags.split(",")
            if character.tags
            else []
        ),
        visibility=character.visibility,
        content_rating=character.content_rating,
        creator_id=character.creator_id,
        creator_username=creator_uname,
        created_at=created_str,
        message_count=msg_count,
        greeting=character.greeting or "",
        personality=character.personality or "",
        scenario=character.scenario or "",
        appearance=character.appearance or "",
        is_builtin=character.is_builtin,
    )


@router.get(
    "",
    response_model=list[CharacterListItem],
)
async def get_characters(
    db: Session = Depends(get_db),
) -> list[CharacterListItem]:

    builtin = [
        CharacterListItem(
            id=character.id,
            name=character.name,
            description=character.description,
            avatar_url=character.avatar_url,
            tags=character.tags,
            visibility=character.visibility,
            content_rating=character.content_rating,
            creator_id=None,
            creator_username="System",
            created_at="2026-01-01",
            message_count=get_character_message_count(db, character.id),
            greeting=character.greeting or "",
            personality=character.personality or "",
            scenario=character.scenario or "",
            appearance=character.appearance or "",
            is_builtin=True,
        )
        for character in list_builtin_characters()
    ]

    database_characters = [
        database_character_to_list_item(
            character,
            db,
        )
        for character in list_database_characters(db)
    ]

    return builtin + database_characters


@router.get(
    "/mine",
    response_model=list[CharacterListItem],
)
async def get_my_characters(
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
) -> list[CharacterListItem]:
    """Returns only the characters created by the current user."""
    from app.db.models import Character as CharacterModel
    characters = (
        db.query(CharacterModel)
        .filter(CharacterModel.creator_id == current_user.id)
        .order_by(CharacterModel.created_at.desc())
        .all()
    )
    return [database_character_to_list_item(c, db) for c in characters]


@router.get(
    "/{character_id}",
    response_model=CharacterDefinition,
)
async def get_character(
    character_id: str,
    db: Session = Depends(get_db),
) -> CharacterDefinition:

    try:
        builtin_char = get_builtin_character(character_id)
        builtin_char.message_count = get_character_message_count(db, character_id)
        builtin_char.creator_username = "System"
        builtin_char.created_at = "2026-01-01"
        return builtin_char
    except CharacterNotFoundError:
        pass

    character = get_database_character(
        db,
        character_id,
    )

    if character is None:
        raise HTTPException(
            status_code=404,
            detail="Character not found",
        )

    return database_character_to_definition(
        character,
        db,
    )


@router.post(
    "",
    response_model=CharacterDefinition,
)
async def create_character(
    character: CharacterDefinition,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
) -> CharacterDefinition:

    character.creator_id = current_user.id

    created = create_database_character(
        db,
        character,
        current_user.id,
    )

    return database_character_to_definition(
        created,
        db,
    )


@router.put(
    "/{character_id}",
    response_model=CharacterDefinition,
)
async def update_character(
    character_id: str,
    character: CharacterDefinition,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
) -> CharacterDefinition:

    try:
        get_builtin_character(character_id)
        raise HTTPException(
            status_code=403,
            detail="Builtin characters cannot be modified",
        )
    except CharacterNotFoundError:
        pass

    existing_character = get_database_character(
        db,
        character_id,
    )

    if existing_character is None:
        raise HTTPException(
            status_code=404,
            detail="Character not found",
        )

    if existing_character.creator_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You cannot modify this character",
        )

    updated = update_database_character(
        db,
        character_id,
        character,
    )

    return database_character_to_definition(
        updated,
        db,
    )


@router.delete(
    "/{character_id}",
)
async def delete_character(
    character_id: str,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    try:
        get_builtin_character(character_id)
        raise HTTPException(
            status_code=403,
            detail="Builtin characters cannot be deleted",
        )
    except CharacterNotFoundError:
        pass

    character = get_database_character(
        db,
        character_id,
    )

    if character is None:
        raise HTTPException(
            status_code=404,
            detail="Character not found",
        )

    if character.creator_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You cannot delete this character",
        )

    deleted = delete_database_character(
        db,
        character_id,
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Character not found",
        )

    return {
        "message": f"{character_id} deleted"
    }