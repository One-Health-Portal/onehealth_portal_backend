from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Optional
import logging

from app.db.connection import get_db
from app.models.hospital_doctor import HospitalDoctor
from app.models.doctor import Doctor
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


@router.post("/hospital-doctor", response_model=HospitalDoctorResponse)
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
        hospital_doctors = (
            db.query(HospitalDoctor)
            .options(joinedload(HospitalDoctor.doctor))
            .filter(HospitalDoctor.hospitalID == hospital_id)
            .all()
        )

        response = []
        for hd in hospital_doctors:
            doctor = hd.doctor
            response.append({
                "hospital_id": hd.hospitalID,
                "doctor_id": hd.doctorID,
                "availability_start_time": hd.availability_start_time,
                "availability_end_time": hd.availability_end_time,
                "profile_picture_url": doctor.profile_picture_url,
                "name": doctor.name,
                "specialization": doctor.specialization,
            })

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

        response = []
        for dh in doctor_hospitals:
            hospital = dh.hospital
            response.append({
                "hospital_id": dh.hospitalID,
                "doctor_id": dh.doctorID,
                "availability_start_time": dh.availability_start_time,
                "availability_end_time": dh.availability_end_time,
                "profile_picture_url": dh.doctor.profile_picture_url,
                "name": dh.doctor.name,
                "specialization": dh.doctor.specialization,
            })

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
    Update an existing hospital-doctor relationship.
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


@router.delete("/hospital-doctor/hospital/{hospital_id}/doctor/{doctor_id}")
async def delete_hospital_doctor(
    hospital_id: int,
    doctor_id: int,
    current_user: dict = Depends(JWTBearer()),
    db: Session = Depends(get_db),
):
    """
    Delete an existing hospital-doctor relationship.
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
