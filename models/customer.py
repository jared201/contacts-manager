from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from uuid import UUID, uuid4
from enum import Enum


class CustomerStatus(str, Enum):
    LEAD = "lead"
    PROSPECT = "prospect"
    CUSTOMER = "customer"
    INACTIVE = "inactive"


class CustomerBase(BaseModel):
    name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    company: Optional[str] = None
    status: CustomerStatus = CustomerStatus.LEAD
    source: Optional[str] = None
    notes: Optional[str] = None


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(CustomerBase):
    name: Optional[str] = None
    status: Optional[CustomerStatus] = None


class Customer(CustomerBase):
    id: UUID = Field(default_factory=uuid4)
    
    class Config:
        from_attributes = True