# CRM System with Dashboard

This repository contains a CRM System API built with FastAPI, featuring a Redis Manager component for data storage and a dashboard built with Jinja2 templates and Bulma CSS.

The Redis Manager handles all CRUD operations with Redis for various models in the system, while the dashboard provides a visual interface for viewing customer and opportunity data.

## Features

### Redis Manager
- Centralized Redis connection management
- Generic CRUD operations for any Pydantic model
- Support for both Pydantic v1 and v2
- Proper serialization and deserialization of models to/from JSON
- Support for querying by field values
- Automatic handling of UUID serialization

### Dashboard
- Interactive dashboard built with Jinja2 templates and Bulma CSS
- Overview of customer and opportunity statistics
- Visual representation of data with pie charts
- Responsive design that works on desktop and mobile devices
- Cards showing customer distribution by status
- Cards showing opportunity distribution by stage
- Recent customers and opportunities tables

## Installation

1. Make sure you have Redis installed and running on your system.
2. Install the required Python packages:

```bash
pip install -r requirements.txt
```

## Usage

### Importing the Redis Manager

```python
from service.redis_manager import redis_manager
```

### Creating a Model Instance

```python
from models.contact import Contact, ContactCreate

# Create a new contact
contact_data = ContactCreate(
    name="John Doe",
    email="john.doe@example.com",
    phone="123-456-7890",
    address="123 Main St, Anytown, USA"
)

# Convert to a Contact model
contact = Contact(**contact_data.dict())

# Store in Redis
redis_manager.create("contact", contact)
```

### Retrieving a Model Instance

```python
from models.contact import Contact

# Get a contact by ID
contact = redis_manager.get("contact", contact_id, Contact)
```

### Retrieving All Model Instances

```python
from models.contact import Contact

# Get all contacts
contacts = redis_manager.get_all("contact", Contact)
```

### Updating a Model Instance

```python
from models.contact import Contact

# Update a contact
update_data = {
    "name": "Jane Doe",
    "email": "jane.doe@example.com"
}
updated_contact = redis_manager.update("contact", contact_id, update_data, Contact)
```

### Deleting a Model Instance

```python
# Delete a contact
success = redis_manager.delete("contact", contact_id)
```

### Querying by Field Value

```python
from models.contact import Contact

# Get contacts by name
contacts = redis_manager.get_by_field("contact", "name", "John Doe", Contact)
```

### Closing the Redis Connection

```python
# Close the Redis connection when done
redis_manager.close()
```

## Integration with Service Modules

The Redis Manager is designed to be easily integrated with existing service modules. Here's an example of how to update a service module to use the Redis Manager:

```python
from typing import List, Optional
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
```

## Configuration

The Redis Manager is configured with default connection parameters (localhost:6379, db=0, no password). To customize these parameters, you can modify the initialization in `service/redis_manager.py`:

```python
# Create a singleton instance of the Redis Manager with custom parameters
redis_manager = RedisManager(
    host='your-redis-host',
    port=6379,
    db=0,
    password='your-redis-password'
)
```

## Running the Application

To run the application with the dashboard:

1. Make sure Redis is running:
```bash
docker run -d -p 6379:6379 redis
```

2. Populate Redis with sample data:
```bash
python populate_redis.py
```

3. Start the FastAPI application:
```bash
uvicorn main:app --reload
```

4. Open your browser and navigate to http://localhost:8000 to view the dashboard.

## API Documentation

FastAPI automatically generates interactive API documentation:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Testing

A test script is provided to verify that the Redis Manager is working correctly:

```bash
python test_redis_manager.py
```

This script tests all CRUD operations for contacts using the Redis Manager.
