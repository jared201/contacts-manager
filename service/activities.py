from typing import List, Optional, Dict
from uuid import UUID
from datetime import datetime

from models.activity import Activity, ActivityCreate, ActivityUpdate, ActivityStatus

# In-memory storage for activities
activities_db: Dict[UUID, Activity] = {}


def get_activities() -> List[Activity]:
    """
    Get all activities.
    """
    return list(activities_db.values())


def get_activity(activity_id: UUID) -> Optional[Activity]:
    """
    Get an activity by ID.
    """
    return activities_db.get(activity_id)


def get_activities_by_customer(customer_id: UUID) -> List[Activity]:
    """
    Get all activities for a specific customer.
    """
    return [act for act in activities_db.values() if act.customer_id == customer_id]


def get_activities_by_opportunity(opportunity_id: UUID) -> List[Activity]:
    """
    Get all activities for a specific opportunity.
    """
    return [act for act in activities_db.values() if act.opportunity_id == opportunity_id]


def create_activity(activity: ActivityCreate) -> Activity:
    """
    Create a new activity.
    """
    # Handle both Pydantic v1 and v2
    activity_data = activity.model_dump() if hasattr(activity, 'model_dump') else activity.dict()
    new_activity = Activity(**activity_data)
    activities_db[new_activity.id] = new_activity
    return new_activity


def update_activity(activity_id: UUID, activity_update: ActivityUpdate) -> Optional[Activity]:
    """
    Update an existing activity.
    """
    if activity_id not in activities_db:
        return None

    # Get the existing activity
    activity = activities_db[activity_id]

    # Update only the fields that are provided
    # Handle both Pydantic v1 and v2
    if hasattr(activity_update, 'model_dump'):
        update_data = activity_update.model_dump(exclude_unset=True)
    else:
        update_data = activity_update.dict(exclude_unset=True)

    for field, value in update_data.items():
        setattr(activity, field, value)

    # If the activity is being marked as completed, set the completed_at timestamp
    if activity.status == ActivityStatus.COMPLETED and not activity.completed_at:
        activity.completed_at = datetime.now()

    # Save the updated activity
    activities_db[activity_id] = activity
    return activity


def delete_activity(activity_id: UUID) -> bool:
    """
    Delete an activity.
    """
    if activity_id not in activities_db:
        return False

    del activities_db[activity_id]
    return True