from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class RecentPatient(BaseModel):
    """Schema for recent patient data"""
    id: int = Field(..., description="User ID of the patient")
    name: str = Field(..., description="Full name of the patient")
    avatar: str = Field(..., description="Avatar URL or placeholder for the patient")
    created_at: str = Field(..., description="Date and time when the account was created (YYYY-MM-DD HH:MM:SS)")

class DepartmentDistribution(BaseModel):
    """Schema for department distribution data"""
    name: str = Field(..., description="Name of the department")
    patients: int = Field(..., description="Number of patients in the department")
    color: str = Field(..., description="Color code for visualization")

class AppointmentAnalytics(BaseModel):
    """Schema for daily appointment analytics"""
    day: str = Field(..., description="Day of the week")
    appointments: int = Field(..., description="Total appointments")
    visits: int = Field(..., description="Completed visits")
    emergency: int = Field(..., description="Emergency cases")

class DashboardResponse(BaseModel):
    """Schema for complete dashboard response"""
    totalAppointments: int = Field(..., description="Total number of appointments")
    activeDoctors: int = Field(..., description="Number of active doctors")
    totalPatients: int = Field(..., description="Total number of patients")
    recentPatients: List[RecentPatient] = Field(
        ..., 
        description="List of recent patients with their details"
    )
    departmentDistribution: List[DepartmentDistribution] = Field(
        ..., 
        description="Distribution of patients across departments"
    )
    appointmentAnalytics: List[AppointmentAnalytics] = Field(
        ..., 
        description="Daily appointment statistics"
    )

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "totalAppointments": 1250,
                "activeDoctors": 45,
                "totalPatients": 3500,
                "recentPatients": [
                    {
                        "id": 1,
                        "name": "John Smith",
                        "avatar": "/api/placeholder/40/40?text=JS",
                        "created_at": "2025-01-21 21:32:04"
                    }
                ],
                "departmentDistribution": [
                    {
                        "name": "Cardiology",
                        "patients": 850,
                        "color": "#FF6384"
                    }
                ],
                "appointmentAnalytics": [
                    {
                        "day": "Monday",
                        "appointments": 45,
                        "visits": 38,
                        "emergency": 7
                    }
                ]
            }
        }