from pydantic import BaseModel, Field, validator
from typing import Optional, Literal, List
from datetime import date, time, datetime

# Base schema for lab tests
class LabTestBase(BaseModel):
    user_id: int
    hospital_id: int
    test_type: str
    test_date: date
    test_time: time  # Store as time object
    status: Optional[Literal["Scheduled", "Completed", "Cancelled"]] = "Scheduled"
    result: Optional[str] = None
    instruction: Optional[str] = None

# Schema for creating a lab test
class LabTestCreate(BaseModel):
    user_id: int
    hospital_id: int
    test_type: str
    test_date: date
    test_time: str  # Accept string input (e.g., "10:00 AM")
    instruction: Optional[str] = None

    @validator("test_time")
    def parse_test_time(cls, value):
        try:
            # Convert "10:00 AM" to a time object
            return datetime.strptime(value, "%I:%M %p").time()
        except ValueError:
            raise ValueError("Invalid time format. Use 'HH:MM AM/PM' (e.g., '10:00 AM').")

# Schema for updating a lab test
class LabTestUpdate(BaseModel):
    test_date: Optional[date] = None
    test_time: Optional[str] = None  # Accept string input (e.g., "10:00 AM")
    status: Optional[Literal["Scheduled", "Completed", "Cancelled"]] = None
    result: Optional[str] = None
    instruction: Optional[str] = None

    @validator("test_time")
    def parse_test_time(cls, value):
        if value is None:
            return None
        try:
            # Convert "10:00 AM" to a time object
            return datetime.strptime(value, "%I:%M %p").time()
        except ValueError:
            raise ValueError("Invalid time format. Use 'HH:MM AM/PM' (e.g., '10:00 AM').")

# Schema for responding with lab test details
class LabTestResponse(BaseModel):
    lab_test_id: int
    user_id: int
    hospital_id: int
    hospital_name: str  # Add this field
    test_type: str
    test_date: date
    test_time: str  # Return as string in "HH:MM AM/PM" format
    status: Optional[Literal["Scheduled", "Completed", "Cancelled"]] = "Scheduled"
    result: Optional[str] = None
    instruction: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

    @validator("test_time", pre=True)
    def format_test_time(cls, value):
        # Convert time object to "HH:MM AM/PM" format
        if isinstance(value, time):
            return value.strftime("%I:%M %p")
        return value

    @validator("updated_at", pre=True)
    def ensure_updated_at(cls, value):
        # Ensure updated_at is not None
        if value is None:
            return datetime.now()
        return value

# Schema for a single time slot
class TimeSlotResponse(BaseModel):
    time: str  # Format: "HH:MM AM/PM"
    available: bool

# Schema for lab test availability response
class LabTestAvailabilityResponse(BaseModel):
    hospital_id: int
    start_time: time
    end_time: time
    time_slots: List[TimeSlotResponse]
    available: bool