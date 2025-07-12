from typing import List, Optional, Dict
from uuid import UUID
from datetime import datetime

from models.note import Note, NoteCreate, NoteUpdate

# In-memory storage for notes
notes_db: Dict[UUID, Note] = {}


def get_notes() -> List[Note]:
    """
    Get all notes.
    """
    return list(notes_db.values())


def get_note(note_id: UUID) -> Optional[Note]:
    """
    Get a note by ID.
    """
    return notes_db.get(note_id)


def get_notes_by_customer(customer_id: UUID) -> List[Note]:
    """
    Get all notes for a specific customer.
    """
    return [note for note in notes_db.values() if note.customer_id == customer_id]


def get_notes_by_opportunity(opportunity_id: UUID) -> List[Note]:
    """
    Get all notes for a specific opportunity.
    """
    return [note for note in notes_db.values() if note.opportunity_id == opportunity_id]


def get_notes_by_activity(activity_id: UUID) -> List[Note]:
    """
    Get all notes for a specific activity.
    """
    return [note for note in notes_db.values() if note.activity_id == activity_id]


def create_note(note: NoteCreate) -> Note:
    """
    Create a new note.
    """
    # Handle both Pydantic v1 and v2
    note_data = note.model_dump() if hasattr(note, 'model_dump') else note.dict()
    new_note = Note(**note_data)
    notes_db[new_note.id] = new_note
    return new_note


def update_note(note_id: UUID, note_update: NoteUpdate) -> Optional[Note]:
    """
    Update an existing note.
    """
    if note_id not in notes_db:
        return None

    # Get the existing note
    note = notes_db[note_id]

    # Update only the fields that are provided
    # Handle both Pydantic v1 and v2
    if hasattr(note_update, 'model_dump'):
        update_data = note_update.model_dump(exclude_unset=True)
    else:
        update_data = note_update.dict(exclude_unset=True)

    for field, value in update_data.items():
        setattr(note, field, value)

    # Update the updated_at timestamp
    note.updated_at = datetime.now()

    # Save the updated note
    notes_db[note_id] = note
    return note


def delete_note(note_id: UUID) -> bool:
    """
    Delete a note.
    """
    if note_id not in notes_db:
        return False

    del notes_db[note_id]
    return True