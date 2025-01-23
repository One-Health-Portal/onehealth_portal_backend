from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Optional
from app.db.connection import get_db
from app.models.user import User
from app.schemas.patient_schema import (
    PatientCreate,
    PatientUpdate,
    PatientResponse,
    PatientStatus,
)
from app.services.supabase_service import SupabaseService
from app.core.jwt_auth import JWTBearer
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/", response_model=List[PatientResponse])
async def get_patients(db: Session = Depends(get_db)):
    """
    Fetch all patients from the database.
    """
    try:
        patients = db.query(User).filter(User.role == "Patient").all()
        return patients
    except Exception as e:
        logger.error(f"Error fetching patients: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch patients")
    
@router.post("/", response_model=PatientResponse, status_code=status.HTTP_201_CREATED)
async def add_patient(
    patient: PatientCreate,
    db: Session = Depends(get_db),
    supabase_service: SupabaseService = Depends(SupabaseService),  # Inject SupabaseService
):
    """
    Add a new patient to the database.
    """
    try:
        # Check for existing user with the same email, phone, or NIC/Passport
        if db.query(User).filter(User.email == patient.email).first():
            raise HTTPException(status_code=400, detail="Email already registered")
        if db.query(User).filter(User.phone == patient.phone).first():
            raise HTTPException(status_code=400, detail="Phone number already registered")
        if db.query(User).filter(User.nic_passport == patient.nic_passport).first():
            raise HTTPException(status_code=400, detail="NIC/Passport already registered")

        # Create user metadata for Supabase
        user_metadata = {
            "first_name": patient.first_name,
            "last_name": patient.last_name,
            "role": "Patient",  # Set the role to "Patient"
            "title": patient.title,
            "phone": patient.phone,
            "id_type": patient.id_type,
            "nic_passport": patient.nic_passport,
        }

        # Create the patient in Supabase
        supabase_response = await supabase_service.sign_up(
            email=patient.email,
            password="default_password",  # Set a default password or generate one
            user_metadata=user_metadata,
        )

        # Extract the Supabase UID from the response
        supabase_uid = supabase_response["supabase_uid"]

        # Create the patient in the local database
        new_patient = User(
            supabase_uid=supabase_uid,  # Save the Supabase UID
            email=patient.email,
            title=patient.title,
            first_name=patient.first_name,
            last_name=patient.last_name,
            phone=patient.phone,
            id_type=patient.id_type,
            nic_passport=patient.nic_passport,
            role="Patient",  # Set the role to "Patient"
        )

        db.add(new_patient)
        db.commit()
        db.refresh(new_patient)
        return new_patient

    except HTTPException as he:
        raise he
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error occurred")
    except Exception as e:
        logger.error(f"Supabase error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create user in Supabase")

# Update a patient
@router.put("/{patient_id}", response_model=PatientResponse)
async def update_patient(
    patient_id: int,
    patient_update: PatientUpdate,
    current_user: User = Depends(JWTBearer()),  # Use User model instead of dict
    db: Session = Depends(get_db),
):
    """
    Update an existing patient's details.
    """
    try:
        # Ensure only Admins or Staff can update patients
        if current_user.role not in ["Admin", "Staff"]:  # Access role directly
            raise HTTPException(status_code=403, detail="Not authorized to update patients")

        # Fetch the patient by ID
        patient = db.query(User).filter(User.user_id == patient_id, User.role == "Patient").first()
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")

        # Update patient fields
        for field, value in patient_update.model_dump(exclude_unset=True).items():
            setattr(patient, field, value)

        db.commit()
        db.refresh(patient)
        return patient

    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error occurred")

# Delete a patient
@router.delete("/{patient_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_patient(
    patient_id: int,
    current_user: User = Depends(JWTBearer()),  # Use User model instead of dict
    db: Session = Depends(get_db),
):
    """
    Delete a patient by ID.
    """
    try:
        # Ensure only Admins or Staff can delete patients
        if current_user.role not in ["Admin", "Staff"]:  # Access role directly
            raise HTTPException(status_code=403, detail="Not authorized to delete patients")

        # Fetch the patient by ID
        patient = db.query(User).filter(User.user_id == patient_id, User.role == "Patient").first()
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")

        # Delete the patient
        db.delete(patient)
        db.commit()
        return

    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error occurred")