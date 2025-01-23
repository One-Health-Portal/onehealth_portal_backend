from pydantic import BaseModel
from datetime import time
from typing import Optional, List

class HospitalDoctorBase(BaseModel):
    hospital_id: int
    doctor_id: int
    availability_start_time: time
    availability_end_time: time

class HospitalDoctorCreate(HospitalDoctorBase):
    pass

class HospitalDoctorUpdate(BaseModel):
    availability_start_time: Optional[time] = None
    availability_end_time: Optional[time] = None

class HospitalDoctorResponse(HospitalDoctorBase):
    profile_picture_url: Optional[str] = None
    name: Optional[str] = None
    specialization: Optional[str] = None

    class Config:
        from_attributes = True

# New schemas for doctor availability and time slots
class TimeSlotResponse(BaseModel):
    time: str
    available: bool

class DoctorAvailabilityResponse(BaseModel):
    start_time: time
    end_time: time
    time_slots: List[TimeSlotResponse]
    available: bool = True