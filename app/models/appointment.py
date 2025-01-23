from sqlalchemy import Column, Integer, ForeignKey, Enum, DateTime, String, Text, Time
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.connection import Base

class Appointment(Base):
    __tablename__ = "appointments"

    # Primary key
    appointment_id = Column(Integer, primary_key=True, index=True)

    # Foreign keys
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)  # ForeignKey to User
    doctor_id = Column(Integer, ForeignKey("doctors.doctor_id"), nullable=False)  # ForeignKey to Doctor
    hospital_id = Column(Integer, ForeignKey("hospitals.hospital_id"), nullable=False)  # ForeignKey to Hospital

    # Appointment details
    appointment_date = Column(DateTime, nullable=False)
    appointment_time = Column(Time, nullable=False)
    status = Column(
        Enum("Pending", "Completed", "Cancelled", name="appointment_status"),
        default="Pending",
        nullable=False
    )  # Enum for appointment status
    note = Column(Text)
    appointment_number = Column(String(20), unique=True, nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="appointments")  # Relationship with User
    doctor = relationship("Doctor", back_populates="appointments")  # Relationship with Doctor
    hospital = relationship("Hospital", back_populates="appointments")  # Relationship with Hospital
    payment = relationship("Payment", back_populates="appointment", uselist=False)  # One-to-one relationship with Payment
