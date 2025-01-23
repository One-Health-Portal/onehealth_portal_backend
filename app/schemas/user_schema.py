from pydantic import BaseModel, EmailStr
from typing import Optional, Literal
from datetime import datetime

class UserBase(BaseModel):
    title: Literal["Mr.", "Mrs.", "Master"]
    first_name: str
    last_name: str
    phone: str
    emergency_contact: Optional[str] = None
    id_type: Literal["NIC", "Passport"]
    nic_passport: str
    email: EmailStr
    role: Optional[Literal["Patient", "Admin", "Staff"]] = "Patient"
    profile_picture_url: Optional[str] = None

class UserCreate(UserBase):
    supabase_uid: str

class UserUpdate(BaseModel):
    title: Optional[Literal["Mr.", "Mrs.", "Master"]] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    emergency_contact: Optional[str] = None
    email: Optional[EmailStr] = None
    profile_picture_url: Optional[str] = None

class UserUpdateDashBoard(BaseModel):
    title: Optional[Literal["Mr.", "Mrs.", "Master"]] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    emergency_contact: Optional[str] = None
    email: Optional[EmailStr] = None
    profile_picture_url: Optional[str] = None
    role: Optional[Literal["Patient", "Admin", "Staff"]] = "Patient"

class UserResponse(UserBase):
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None  # Make updated_at optional

    class Config:
        from_attributes = True