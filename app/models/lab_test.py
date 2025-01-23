from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Enum, Date, Time
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.connection import Base

class LabTest(Base):
    __tablename__ = "lab_tests"

    lab_test_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    hospital_id = Column(Integer, ForeignKey("hospitals.hospital_id"), nullable=False)
    test_type = Column(String(100), nullable=False)
    test_date = Column(Date, nullable=False)
    test_time = Column(Time, nullable=False)
    status = Column(Enum("Scheduled", "Completed", "Cancelled"), default="Scheduled")
    result = Column(Text)
    instruction = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Define relationship to Hospital
    hospital = relationship("Hospital", back_populates="lab_tests")