from typing import List, Optional, Dict
from uuid import UUID

from models.customer import Customer, CustomerCreate, CustomerUpdate
from service.redis_manager import redis_manager

# Model type for Redis keys
CUSTOMER_MODEL_TYPE = "customer"


def get_customers() -> List[Customer]:
    """
    Get all customers.
    """
    return redis_manager.get_all(CUSTOMER_MODEL_TYPE, Customer)


def get_customer(customer_id: UUID) -> Optional[Customer]:
    """
    Get a customer by ID.
    """
    return redis_manager.get(CUSTOMER_MODEL_TYPE, customer_id, Customer)


def create_customer(customer: CustomerCreate) -> Customer:
    """
    Create a new customer.
    """
    # Handle both Pydantic v1 and v2
    customer_data = customer.model_dump() if hasattr(customer, 'model_dump') else customer.dict()
    new_customer = Customer(**customer_data)
    return redis_manager.create(CUSTOMER_MODEL_TYPE, new_customer)


def update_customer(customer_id: UUID, customer_update: CustomerUpdate) -> Optional[Customer]:
    """
    Update an existing customer.
    """
    # Handle both Pydantic v1 and v2
    if hasattr(customer_update, 'model_dump'):
        update_data = customer_update.model_dump(exclude_unset=True)
    else:
        update_data = customer_update.dict(exclude_unset=True)

    return redis_manager.update(CUSTOMER_MODEL_TYPE, customer_id, update_data, Customer)


def delete_customer(customer_id: UUID) -> bool:
    """
    Delete a customer.
    """
    return redis_manager.delete(CUSTOMER_MODEL_TYPE, customer_id)
