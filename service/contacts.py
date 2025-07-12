from typing import List, Optional, Dict
from uuid import UUID

from models.contact import Contact, ContactCreate, ContactUpdate
from service.redis_manager import redis_manager

# Model type for Redis keys
MODEL_TYPE = "contact"


def get_contacts() -> List[Contact]:
    """
    Get all contacts.
    """
    return redis_manager.get_all(MODEL_TYPE, Contact)


def get_contact(contact_id: UUID) -> Optional[Contact]:
    """
    Get a contact by ID.
    """
    return redis_manager.get(MODEL_TYPE, contact_id, Contact)


def create_contact(contact: ContactCreate) -> Contact:
    """
    Create a new contact.
    """
    # Handle both Pydantic v1 and v2
    contact_data = contact.model_dump() if hasattr(contact, 'model_dump') else contact.dict()
    new_contact = Contact(**contact_data)
    return redis_manager.create(MODEL_TYPE, new_contact)


def update_contact(contact_id: UUID, contact_update: ContactUpdate) -> Optional[Contact]:
    """
    Update an existing contact.
    """
    # Handle both Pydantic v1 and v2
    if hasattr(contact_update, 'model_dump'):
        update_data = contact_update.model_dump(exclude_unset=True)
    else:
        update_data = contact_update.dict(exclude_unset=True)

    return redis_manager.update(MODEL_TYPE, contact_id, update_data, Contact)


def delete_contact(contact_id: UUID) -> bool:
    """
    Delete a contact.
    """
    return redis_manager.delete(MODEL_TYPE, contact_id)
