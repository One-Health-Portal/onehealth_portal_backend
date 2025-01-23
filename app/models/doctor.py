from sqlalchemy import Column, Integer, String, Enum, DateTime, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.connection import Base

class Doctor(Base):
    __tablename__ = "doctors"

    doctor_id = Column(Integer, primary_key=True, index=True)
    title = Column(Enum("Dr.", "Prof."), nullable=False)
    name = Column(String(100), nullable=False)
    specialization = Column(String(100))
    profile_picture_url = Column(String(255))
    is_active = Column(Boolean, default=True)  # Add this new column
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Define relationship to Appointment
    appointments = relationship("Appointment", back_populates="doctor")

    # Define relationship to HospitalDoctor
    hospital_doctors = relationship("HospitalDoctor", back_populates="doctor")