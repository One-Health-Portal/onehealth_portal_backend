from pydantic import BaseModel, Field
from typing import Optional, Literal, List
from datetime import datetime

# Schema for hospital availability
class Availability(BaseModel):
    start: str = Field(example="09:00")  # Example: "09:00"
    end: str = Field(example="17:00")    # Example: "17:00"

# Schema for hospital details
class HospitalResponse(BaseModel):
    hospital_id: int
    name: str
    logo_url: Optional[str] = Field(default=None, example="https://example.com/logo.jpg")
    address: str
    availability: Availability
    emergency_services_available: bool

# Base schema for doctor
class DoctorBase(BaseModel):
    title: Literal["Dr.", "Prof."]
    name: str
    specialization: Optional[str] = Field(default=None, example="Cardiologist")
    profile_picture_url: Optional[str] = Field(default=None, example="https://example.com/profile.jpg")

# Schema for creating a doctor
class DoctorCreate(DoctorBase):
    pass

# Schema for updating a doctor
class DoctorUpdate(BaseModel):
    title: Optional[Literal["Dr.", "Prof."]] = Field(default=None, example="Dr.")
    name: Optional[str] = Field(default=None, example="John Doe")
    specialization: Optional[str] = Field(default=None, example="Cardiologist")
    profile_picture_url: Optional[str] = Field(default=None, example="https://example.com/profile.jpg")

# Schema for doctor response (includes hospitals)
class DoctorResponse(DoctorBase):
    doctor_id: int
    created_at: datetime
    updated_at: datetime
    hospitals: List[HospitalResponse]  # List of associated hospitals

    class Config:
        from_attributes = True  # Enable ORM mode for SQLAlchemy compatibility