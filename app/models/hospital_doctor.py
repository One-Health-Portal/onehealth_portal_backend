from sqlalchemy import Column, Integer, ForeignKey, Time
from sqlalchemy.orm import relationship
from app.db.connection import Base

class HospitalDoctor(Base):
    __tablename__ = "hospitaldoctor"

    hospitalID = Column(Integer, ForeignKey("hospitals.hospital_id"), primary_key=True)
    doctorID = Column(Integer, ForeignKey("doctors.doctor_id"), primary_key=True)
    availability_start_time = Column(Time, nullable=False)
    availability_end_time = Column(Time, nullable=False)

    # Define relationship to Doctor
    doctor = relationship("Doctor", back_populates="hospital_doctors")

    # Define relationship to Hospital
    hospital = relationship("Hospital", back_populates="hospital_doctors")