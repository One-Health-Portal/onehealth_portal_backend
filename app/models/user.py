from sqlalchemy import Column, Integer, String, Enum, DateTime, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship  # Import relationship
from app.db.connection import Base
from pydantic import BaseModel  # Import BaseModel from Pydantic

class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    supabase_uid = Column(String(36), unique=True, nullable=False)
    title = Column(Enum("Mr.", "Mrs.", "Master"), nullable=False)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    phone = Column(String(15), unique=True, nullable=False)
    emergency_contact = Column(String(15))
    id_type = Column(Enum("NIC", "Passport"), nullable=False)
    nic_passport = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    role = Column(Enum("Patient", "Admin", "Staff"), default="Patient")
    profile_picture_url = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    two_factor_enabled = Column(Boolean, default=False)  # Add this column
    two_factor_method = Column(String(10))  # Add this column
    # Relationship with appointments
    appointments = relationship("Appointment", back_populates="user")

# Pydantic model for JWT payload
class UserPayload(BaseModel):
    user_id: int
    role: str