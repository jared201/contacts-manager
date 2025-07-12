from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID, uuid4
from datetime import datetime


class NoteBase(BaseModel):
    content: str
    customer_id: Optional[UUID] = None
    opportunity_id: Optional[UUID] = None
    activity_id: Optional[UUID] = None
    created_by: Optional[str] = None  # In a real system, this would be a user ID


class NoteCreate(NoteBase):
    pass


class NoteUpdate(NoteBase):
    content: Optional[str] = None
    customer_id: Optional[UUID] = None
    opportunity_id: Optional[UUID] = None
    activity_id: Optional[UUID] = None


class Note(NoteBase):
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        from_attributes = True