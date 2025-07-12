import uuid
from models.contact import ContactCreate, Contact
from service.contacts import create_contact, get_contact, get_contacts, update_contact, delete_contact
from service.redis_manager import redis_manager

def test_contact_crud():
    """
    Test CRUD operations for contacts using the Redis Manager.
    """
    print("Testing Contact CRUD operations with Redis Manager...")
    
    # Create a contact
    contact_data = ContactCreate(
        name="John Doe",
        email="john.doe@example.com",
        phone="123-456-7890",
        address="123 Main St, Anytown, USA"
    )
    
    created_contact = create_contact(contact_data)
    print(f"Created contact: {created_contact}")
    
    # Get the contact by ID
    retrieved_contact = get_contact(created_contact.id)
    print(f"Retrieved contact: {retrieved_contact}")
    
    # Update the contact
    from models.contact import ContactUpdate
    update_data = ContactUpdate(
        name="Jane Doe",
        email="jane.doe@example.com"
    )
    
    updated_contact = update_contact(created_contact.id, update_data)
    print(f"Updated contact: {updated_contact}")
    
    # Get all contacts
    all_contacts = get_contacts()
    print(f"All contacts: {all_contacts}")
    
    # Delete the contact
    deleted = delete_contact(created_contact.id)
    print(f"Contact deleted: {deleted}")
    
    # Verify deletion
    deleted_contact = get_contact(created_contact.id)
    print(f"Contact after deletion: {deleted_contact}")
    
    # Clean up
    redis_manager.close()
    
    print("Test completed.")

if __name__ == "__main__":
    test_contact_crud()