from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Optional
from datetime import datetime, time, timedelta, date
import logging
from sqlalchemy import func

from app.db.connection import get_db
from app.models.appointment import Appointment
from app.models.hospital_doctor import HospitalDoctor
from app.models.doctor import Doctor
from app.models.hospital import Hospital
from app.schemas.dashboard_doctor_schema import DashboardDoctorResponse
from app.schemas.doctor_schema import DoctorCreate, DoctorResponse, DoctorUpdate
from app.schemas.hospital_doctor_schema import (
    DoctorAvailabilityResponse,
    HospitalDoctorCreate,
    HospitalDoctorUpdate,
    HospitalDoctorResponse,
    TimeSlotResponse,
)
from app.core.jwt_auth import JWTBearer

logger = logging.getLogger(__name__)
router = APIRouter()

def generate_time_slots(start_time: time, end_time: time) -> List[TimeSlotResponse]:
    """
    Generate time slots between start and end times.
    """
    slots = []
    current_datetime = datetime.combine(datetime.today(), start_time)
    end_datetime = datetime.combine(datetime.today(), end_time)

    while current_datetime < end_datetime:
        slots.append(TimeSlotResponse(
            time=current_datetime.strftime("%I:%M %p"),
            available=True
        ))
        current_datetime += timedelta(minutes=30)

    return slots

@router.get("/dashboard/doctors/{doctor_id}", response_model=DoctorResponse)
async def get_doctor_details(
    doctor_id: int,
    db: Session = Depends(get_db)
):
    """
    Retrieve detailed information for a specific doctor, including statistics.
    """
    try:
        # Fetch the doctor details
        doctor = db.query(Doctor).options(joinedload(Doctor.appointments)).filter(Doctor.doctor_id == doctor_id).first()

        if not doctor:
            raise HTTPException(status_code=404, detail="Doctor not found")

        # Calculate statistics
        active_patients = db.query(func.count(Appointment.appointment_id)).filter(
            Appointment.doctor_id == doctor_id,
            Appointment.status == "Completed"
        ).scalar()

        total_appointments = db.query(func.count(Appointment.appointment_id)).filter(
            Appointment.doctor_id == doctor_id
        ).scalar()

        # Prepare the response
        return {
            "doctor_id": doctor.doctor_id,
            "name": doctor.name,
            "specialization": doctor.specialization,
            "profile_picture_url": doctor.profile_picture_url,
            "contact": doctor.contact,
            "email": doctor.email,
            "status": "Active",  # Default status; update if dynamic status exists
            "patients": active_patients,
            "total_appointments": total_appointments,
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while retrieving doctor details: {str(e)}"
        )

@router.get("/", response_model=List[DashboardDoctorResponse])
async def get_all_doctors(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(JWTBearer())
):
    """
    Retrieve all doctors for the dashboard, including patient count.
    """
    try:
        doctors = db.query(
            Doctor,
            func.count(Appointment.appointment_id).label("patient_count")
        ).join(
            Appointment, Appointment.doctor_id == Doctor.doctor_id, isouter=True
        ).group_by(
            Doctor.doctor_id
        ).offset(skip).limit(limit).all()

        response = [
            DashboardDoctorResponse(
                doctor_id=doctor.doctor_id,
                title=doctor.title,  # Ensure title is included
                name=doctor.name,
                specialization=doctor.specialization,
                profile_picture_url=doctor.profile_picture_url,
                created_at=doctor.created_at,
                updated_at=doctor.updated_at,
                status="Active",
                patients=patient_count,
            )
            for doctor, patient_count in doctors
        ]

        return response
    except Exception as e:
        logger.error(f"Error during database session: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Could not retrieve doctors: {str(e)}"
        )


@router.post("/dashboard/doctors/", response_model=DoctorResponse)
async def create_doctor(
    doctor: DoctorCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(JWTBearer())
):
    """
    Create a new doctor in the dashboard.
    """
    try:
        # Check if the current user has the necessary role
        if current_user.get("role") not in ["Admin", "Staff"]:
            raise HTTPException(
                status_code=403,
                detail="Only admin and staff can create doctors.",
            )

        # Create a new doctor instance
        new_doctor = Doctor(**doctor.dict())

        # Add the new doctor to the database
        db.add(new_doctor)
        db.commit()
        db.refresh(new_doctor)

        return new_doctor
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while creating the doctor: {str(e)}",
        )

@router.put("/dashboard/doctors/{doctor_id}", response_model=DoctorResponse)
async def update_doctor(
    doctor_id: int,
    doctor: DoctorUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(JWTBearer())
):
    """
    Update a doctor's name in the dashboard.
    """
    try:
        # Check if the current user has the necessary role
        if current_user.get("role") not in ["Admin", "Staff"]:
            raise HTTPException(
                status_code=403,
                detail="Only admin and staff can update doctors.",
            )

        # Fetch the doctor from the database
        existing_doctor = db.query(Doctor).filter(Doctor.doctor_id == doctor_id).first()
        if not existing_doctor:
            raise HTTPException(status_code=404, detail="Doctor not found.")

        # Update the doctor's name
        if doctor.name:
            existing_doctor.name = doctor.name

        db.commit()
        db.refresh(existing_doctor)

        return existing_doctor
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while updating the doctor: {str(e)}",
        )

@router.get("/doctor/{doctor_id}/availability", response_model=DoctorAvailabilityResponse)
async def get_doctor_availability(
    doctor_id: int,
    hospital_id: int,
    selected_date: Optional[date] = None,
    current_user: dict = Depends(JWTBearer()),
    db: Session = Depends(get_db)
):
    """
    Retrieve doctor's availability for a specific hospital.
    """
    try:
        # Query the hospitaldoctor table to get availability
        availability = db.query(HospitalDoctor).filter(
            HospitalDoctor.doctorID == doctor_id,
            HospitalDoctor.hospitalID == hospital_id
        ).first()

        if not availability:
            # If no specific availability found, return default times
            default_start = time(9, 0)
            default_end = time(17, 0)
            return DoctorAvailabilityResponse(
                start_time=default_start,
                end_time=default_end,
                time_slots=generate_time_slots(default_start, default_end),
                available=True
            )

        # Check for existing appointments on the selected date
        time_slots = generate_time_slots(
            availability.availability_start_time, 
            availability.availability_end_time
        )

        if selected_date:
            existing_appointments = db.query(Appointment).filter(
                Appointment.doctor_id == doctor_id,
                Appointment.hospital_id == hospital_id,
                Appointment.appointment_date == selected_date
            ).all()

            # Mark slots as unavailable if already booked
            for appointment in existing_appointments:
                for slot in time_slots:
                    if slot.time == appointment.appointment_time.strftime("%I:%M %p"):
                        slot.available = False

        return DoctorAvailabilityResponse(
            start_time=availability.availability_start_time,
            end_time=availability.availability_end_time,
            time_slots=time_slots,
            available=True
        )

    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Could not retrieve doctor availability")

@router.get("/doctor/{doctor_id}/booking-preparation")
async def prepare_doctor_booking(
    doctor_id: int,
    current_user: dict = Depends(JWTBearer()),
    db: Session = Depends(get_db)
):
    """
    Retrieve hospitals and initial booking information for a doctor.
    """
    try:
        # Get hospitals where the doctor is available
        doctor_hospitals = (
            db.query(HospitalDoctor)
            .options(joinedload(HospitalDoctor.hospital))
            .filter(HospitalDoctor.doctorID == doctor_id)
            .all()
        )

        # Format the response
        hospitals = []
        for dh in doctor_hospitals:
            hospital = dh.hospital
            hospitals.append({
                "hospital_id": hospital.hospital_id,
                "name": hospital.name,
                "address": hospital.address,
                "logo_url": hospital.logo_url,
                "emergency_services": hospital.emergency_services_available,
                "start_time": dh.availability_start_time,
                "end_time": dh.availability_end_time
            })

        return {
            "hospitals": hospitals
        }

    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Could not prepare doctor booking")

@router.post("/", response_model=HospitalDoctorResponse)
async def create_hospital_doctor(
    hospital_doctor: HospitalDoctorCreate,
    current_user: dict = Depends(JWTBearer()),
    db: Session = Depends(get_db),
):
    """
    Create a new hospital-doctor relationship.
    """
    try:
        if current_user.get("role") not in ["Admin", "Staff"]:
            raise HTTPException(
                status_code=403,
                detail="Only admin and staff can manage hospital-doctor relationships",
            )

        new_hospital_doctor = HospitalDoctor(**hospital_doctor.model_dump())
        db.add(new_hospital_doctor)
        db.commit()
        db.refresh(new_hospital_doctor)
        return new_hospital_doctor
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Could not create hospital-doctor relationship")

@router.get("/hospital/{hospital_id}/doctors", response_model=List[HospitalDoctorResponse])
async def get_hospital_doctors(
    hospital_id: int,
    current_user: dict = Depends(JWTBearer()),
    db: Session = Depends(get_db),
):
    """
    Retrieve all doctors associated with a specific hospital.
    """
    try:
        # Join the Doctor table and fetch required fields
        hospital_doctors = (
            db.query(HospitalDoctor)
            .options(joinedload(HospitalDoctor.doctor))
            .filter(HospitalDoctor.hospitalID == hospital_id)
            .all()
        )

        # Format the response to include doctor details
        response = []
        for hd in hospital_doctors:
            doctor = hd.doctor
            response.append(HospitalDoctorResponse(
                hospital_id=hd.hospitalID,
                doctor_id=hd.doctorID,
                availability_start_time=hd.availability_start_time,
                availability_end_time=hd.availability_end_time,
                profile_picture_url=doctor.profile_picture_url,
                name=doctor.name,
                specialization=doctor.specialization,
            ))

        return response
    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Could not retrieve hospital doctors")

@router.get("/doctor/{doctor_id}/hospitals", response_model=List[HospitalDoctorResponse])
async def get_doctor_hospitals(
    doctor_id: int,
    current_user: dict = Depends(JWTBearer()),
    db: Session = Depends(get_db),
):
    """
    Retrieve all hospitals associated with a specific doctor.
    """
    try:
        doctor_hospitals = (
            db.query(HospitalDoctor)
            .options(joinedload(HospitalDoctor.hospital))
            .filter(HospitalDoctor.doctorID == doctor_id)
            .all()
        )

        # Format the response to include hospital details
        response = []
        for dh in doctor_hospitals:
            hospital = dh.hospital
            response.append(HospitalDoctorResponse(
                hospital_id=dh.hospitalID,
                doctor_id=dh.doctorID,
                availability_start_time=dh.availability_start_time,
                availability_end_time=dh.availability_end_time,
                profile_picture_url=dh.doctor.profile_picture_url,
                name=dh.doctor.name,
                specialization=dh.doctor.specialization,
            ))

        return response
    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Could not retrieve doctor hospitals")

@router.put("/hospital/{hospital_id}/doctor/{doctor_id}", response_model=HospitalDoctorResponse)
async def update_hospital_doctor(
    hospital_id: int,
    doctor_id: int,
    hospital_doctor_update: HospitalDoctorUpdate,
    current_user: dict = Depends(JWTBearer()),
    db: Session = Depends(get_db),
):
    """
    Update a hospital-doctor relationship.
    """
    try:
        if current_user.get("role") not in ["Admin", "Staff"]:
            raise HTTPException(
                status_code=403,
                detail="Only admin and staff can update hospital-doctor relationships",
            )

        hospital_doctor = (
            db.query(HospitalDoctor)
            .filter(
                HospitalDoctor.hospitalID == hospital_id,
                HospitalDoctor.doctorID == doctor_id,
            )
            .first()
        )

        if not hospital_doctor:
            raise HTTPException(status_code=404, detail="Hospital-doctor relationship not found")

        for field, value in hospital_doctor_update.model_dump(exclude_unset=True).items():
            setattr(hospital_doctor, field, value)

        db.commit()
        db.refresh(hospital_doctor)
        return hospital_doctor
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Could not update hospital-doctor relationship")

@router.delete("/hospital/{hospital_id}/doctor/{doctor_id}")
async def delete_hospital_doctor(
    hospital_id: int,
    doctor_id: int,
    current_user: dict = Depends(JWTBearer()),
    db: Session = Depends(get_db),
):
    """
    Delete a hospital-doctor relationship.
    """
    try:
        if current_user.get("role") not in ["Admin", "Staff"]:
            raise HTTPException(
                status_code=403,
                detail="Only admin and staff can delete hospital-doctor relationships",
            )

        hospital_doctor = (
            db.query(HospitalDoctor)
            .filter(
                HospitalDoctor.hospitalID == hospital_id,
                HospitalDoctor.doctorID == doctor_id,
            )
            .first()
        )

        if not hospital_doctor:
            raise HTTPException(status_code=404, detail="Hospital-doctor relationship not found")

        db.delete(hospital_doctor)
        db.commit()
        return {"message": "Hospital-doctor relationship deleted successfully"}
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Could not delete hospital-doctor relationship")