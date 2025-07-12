from typing import List, Optional, Dict
from uuid import UUID
from datetime import datetime

from models.opportunity import Opportunity, OpportunityCreate, OpportunityUpdate
from service.redis_manager import redis_manager

# Model type for Redis keys
OPPORTUNITY_MODEL_TYPE = "opportunity"


def get_opportunities() -> List[Opportunity]:
    """
    Get all opportunities.
    """
    return redis_manager.get_all(OPPORTUNITY_MODEL_TYPE, Opportunity)


def get_opportunity(opportunity_id: UUID) -> Optional[Opportunity]:
    """
    Get an opportunity by ID.
    """
    return redis_manager.get(OPPORTUNITY_MODEL_TYPE, opportunity_id, Opportunity)


def get_opportunities_by_customer(customer_id: UUID) -> List[Opportunity]:
    """
    Get all opportunities for a specific customer.
    """
    return redis_manager.get_by_field(OPPORTUNITY_MODEL_TYPE, "customer_id", customer_id, Opportunity)


def create_opportunity(opportunity: OpportunityCreate) -> Opportunity:
    """
    Create a new opportunity.
    """
    # Handle both Pydantic v1 and v2
    opportunity_data = opportunity.model_dump() if hasattr(opportunity, 'model_dump') else opportunity.dict()
    new_opportunity = Opportunity(**opportunity_data)
    return redis_manager.create(OPPORTUNITY_MODEL_TYPE, new_opportunity)


def update_opportunity(opportunity_id: UUID, opportunity_update: OpportunityUpdate) -> Optional[Opportunity]:
    """
    Update an existing opportunity.
    """
    # Handle both Pydantic v1 and v2
    if hasattr(opportunity_update, 'model_dump'):
        update_data = opportunity_update.model_dump(exclude_unset=True)
    else:
        update_data = opportunity_update.dict(exclude_unset=True)

    # Add updated_at to the update data
    update_data["updated_at"] = datetime.now()

    return redis_manager.update(OPPORTUNITY_MODEL_TYPE, opportunity_id, update_data, Opportunity)


def delete_opportunity(opportunity_id: UUID) -> bool:
    """
    Delete an opportunity.
    """
    return redis_manager.delete(OPPORTUNITY_MODEL_TYPE, opportunity_id)
