from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.connection import Base

class Hospital(Base):
    __tablename__ = "hospitals"

    hospital_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    address = Column(Text)
    phone = Column(String(15))
    emergency_services_available = Column(Boolean, default=False)
    logo_url = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Define relationship to Appointment
    appointments = relationship("Appointment", back_populates="hospital")

    # Define relationship to LabTest
    lab_tests = relationship("LabTest", back_populates="hospital")

    # Define relationship to HospitalDoctor
    hospital_doctors = relationship("HospitalDoctor", back_populates="hospital")