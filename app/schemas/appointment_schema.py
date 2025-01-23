from pydantic import BaseModel, Field, validator
from datetime import date, datetime, time
from typing import Optional, List, Literal

# Appointment Schemas
class AppointmentBase(BaseModel):
    user_id: int = Field(..., description="ID of the user booking the appointment")
    doctor_id: int = Field(..., description="ID of the doctor")
    hospital_id: int = Field(..., description="ID of the hospital")
    appointment_date: date = Field(..., description="Date of the appointment")
    appointment_time: str = Field(..., description="Time of the appointment in HH:MM AM/PM format")
    status: Optional[Literal["Pending", "Completed", "Cancelled"]] = "Pending"
    note: Optional[str] = Field(None, max_length=500, description="Additional notes for the appointment")
    appointment_number: str = Field(..., min_length=8, max_length=20, description="Unique appointment identifier")

class AppointmentCreateRequest(BaseModel):
    """
    Schema for creating a new appointment via API request
    """
    doctor_id: int = Field(..., description="ID of the doctor")
    hospital_id: int = Field(..., description="ID of the hospital")
    appointment_date: date = Field(..., description="Date of the appointment")
    appointment_time: str = Field(..., description="Time of the appointment in HH:MM AM/PM format")
    note: Optional[str] = Field(None, max_length=500, description="Additional notes for the appointment")

    @validator('appointment_date')
    def validate_appointment_date(cls, v):
        """
        Ensure appointment date is not in the past
        """
        if v < date.today():
            raise ValueError("Appointment date cannot be in the past")
        return v

    @validator('appointment_time')
    def validate_time_format(cls, v):
        """
        Validate time format
        """
        try:
            datetime.strptime(v, "%I:%M %p")
            return v
        except ValueError:
            raise ValueError("Time must be in 'HH:MM AM/PM' format")

class AppointmentResponse(BaseModel):
    appointment_id: int
    user_id: int
    doctor_id: int
    hospital_id: int
    appointment_date: date
    appointment_time: str
    status: str
    note: Optional[str] = None
    appointment_number: str
    created_at: datetime
    updated_at: datetime
    payment_status: Optional[str] = None
    total_amount: Optional[float] = Field(default=0.0)
    doctor_name: Optional[str] = None
    doctor_specialization: Optional[str] = None
    hospital_name: Optional[str] = None
    user_name: Optional[str] = None  # Added field for user's full name
    user_email: Optional[str] = None  # Optional user email
    user_phone: Optional[str] = None  # Optional user phone

    @validator('appointment_time', pre=True)
    def format_appointment_time(cls, v):
        """
        Convert datetime.time to string in "HH:MM AM/PM" format
        """
        if isinstance(v, time):
            return v.strftime("%I:%M %p")
        return v

    class Config:
        from_attributes = True

class AppointmentUpdate(BaseModel):
    """
    Schema for updating an existing appointment
    """
    status: Optional[Literal["Pending", "Completed", "Cancelled"]] = None
    note: Optional[str] = Field(None, max_length=500)

# Time Slot Schemas
class TimeSlotResponse(BaseModel):
    time: str  # Format as string (e.g., "09:00 AM")
    available: bool  # Indicates whether the slot is available

class AvailableTimeSlotsResponse(BaseModel):
    available_slots: List[TimeSlotResponse]  # List of available time slots
    unavailable_slots: List[TimeSlotResponse]  # List of unavailable time slots
    appointments: List[AppointmentResponse]  # List of formatted appointments

# Doctor Hospitals Response Schema
class DoctorHospitalsResponse(BaseModel):
    hospital_id: int
    name: str
    address: str
    logo_url: Optional[str] = None
    emergency_services_available: bool
    availability_start: str  # Format as string (e.g., "09:00 AM")
    availability_end: str  # Format as string (e.g., "05:00 PM")