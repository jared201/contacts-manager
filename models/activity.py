from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID, uuid4
from enum import Enum
from datetime import datetime


class ActivityType(str, Enum):
    CALL = "call"
    EMAIL = "email"
    MEETING = "meeting"
    TASK = "task"
    NOTE = "note"


class ActivityStatus(str, Enum):
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELED = "canceled"


class ActivityBase(BaseModel):
    title: str
    description: Optional[str] = None
    activity_type: ActivityType
    status: ActivityStatus = ActivityStatus.PLANNED
    due_date: Optional[datetime] = None
    customer_id: Optional[UUID] = None
    opportunity_id: Optional[UUID] = None
    assigned_to: Optional[str] = None  # In a real system, this would be a user ID


class ActivityCreate(ActivityBase):
    pass


class ActivityUpdate(ActivityBase):
    title: Optional[str] = None
    activity_type: Optional[ActivityType] = None
    status: Optional[ActivityStatus] = None
    customer_id: Optional[UUID] = None
    opportunity_id: Optional[UUID] = None


class Activity(ActivityBase):
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True