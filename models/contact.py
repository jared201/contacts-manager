from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from uuid import UUID, uuid4


class ContactBase(BaseModel):
    name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None


class ContactCreate(ContactBase):
    pass


class ContactUpdate(ContactBase):
    name: Optional[str] = None


class Contact(ContactBase):
    id: UUID = Field(default_factory=uuid4)

    class Config:
        from_attributes = True
