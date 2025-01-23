from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime

class DashboardDoctorBase(BaseModel):
    """
    Base schema for dashboard doctor.
    """
    title: Literal["Dr.", "Prof."] = Field(description="Title of the doctor (e.g., Dr., Prof.).")
    name: str = Field(description="Full name of the doctor.")
    specialization: Optional[str] = Field(default=None, example="Cardiologist", description="Specialization of the doctor.")
    profile_picture_url: Optional[str] = Field(default=None, example="https://example.com/profile.jpg", description="URL of the doctor's profile picture.")
    status: str = Field(default="Active", description="Status of the doctor (e.g., Active, Inactive).")
    patients: int = Field(default=0, description="Number of patients associated with the doctor.")

class DashboardDoctorCreate(DashboardDoctorBase):
    """
    Schema for creating a new doctor in the dashboard.
    """
    pass

class DashboardDoctorUpdate(BaseModel):
    """
    Schema for updating a doctor in the dashboard.
    Only the name can be updated.
    """
    name: Optional[str] = Field(default=None, example="John Doe", description="Updated name of the doctor.")

class DashboardDoctorResponse(DashboardDoctorBase):
    """
    Schema for the response when fetching a doctor from the dashboard.
    Includes additional fields like `doctor_id`, `created_at`, and `updated_at`.
    """
    doctor_id: int = Field(description="Unique identifier for the doctor.")
    created_at: datetime = Field(description="Timestamp when the doctor was created.")
    updated_at: datetime = Field(description="Timestamp when the doctor was last updated.")

    class Config:
        from_attributes = True  # Enable ORM mode for SQLAlchemy compatibility
