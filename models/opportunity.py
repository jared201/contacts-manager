from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID, uuid4
from enum import Enum
from datetime import datetime


class OpportunityStage(str, Enum):
    QUALIFICATION = "qualification"
    NEEDS_ANALYSIS = "needs_analysis"
    PROPOSAL = "proposal"
    NEGOTIATION = "negotiation"
    CLOSED_WON = "closed_won"
    CLOSED_LOST = "closed_lost"


class OpportunityBase(BaseModel):
    name: str
    customer_id: UUID
    amount: Optional[float] = None
    stage: OpportunityStage = OpportunityStage.QUALIFICATION
    expected_close_date: Optional[datetime] = None
    probability: Optional[int] = None  # 0-100%
    description: Optional[str] = None


class OpportunityCreate(OpportunityBase):
    pass


class OpportunityUpdate(OpportunityBase):
    name: Optional[str] = None
    customer_id: Optional[UUID] = None
    stage: Optional[OpportunityStage] = None


class Opportunity(OpportunityBase):
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        from_attributes = True