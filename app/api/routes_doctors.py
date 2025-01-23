from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, and_
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Optional
from app.db.connection import get_db
from app.models.doctor import Doctor
from app.schemas.doctor_schema import DoctorCreate, DoctorUpdate, DoctorResponse
from app.models.hospital_doctor import HospitalDoctor
from app.models.hospital import Hospital
from app.core.jwt_auth import JWTBearer
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/", response_model=List[DoctorResponse])
async def get_doctors_with_hospitals(
    specialization: Optional[str] = Query(None, description="Filter by specialization"),
    hospital_id: Optional[int] = Query(None, description="Filter by hospital ID"),
    db: Session = Depends(get_db)
):
    """
    Retrieve all doctors with optional filtering by specialization and hospital ID.
    Includes associated hospitals for each doctor with their actual availability times.
    """
    try:
        # Base query to fetch doctors
        query = db.query(Doctor)

        # Apply specialization filter if provided
        if specialization:
            query = query.filter(Doctor.specialization == specialization)

        # Apply hospital filter if provided
        if hospital_id:
            query = query.join(HospitalDoctor).filter(HospitalDoctor.hospitalID == hospital_id)

        # Execute the query and fetch doctors
        doctors = query.all()

        # Fetch associated hospitals and availability for each doctor
        doctors_with_hospitals = []
        for doctor in doctors:
            # Query to get hospitals with availability times
            hospitals_data = db.query(
                Hospital,
                HospitalDoctor.availability_start_time,
                HospitalDoctor.availability_end_time
            ).join(
                HospitalDoctor,
                Hospital.hospital_id == HospitalDoctor.hospitalID
            ).filter(
                HospitalDoctor.doctorID == doctor.doctor_id
            ).all()

            # Format hospital data with actual availability times
            hospital_list = []
            for hospital, start_time, end_time in hospitals_data:
                hospital_list.append({
                    "hospital_id": hospital.hospital_id,
                    "name": hospital.name,
                    "logo_url": hospital.logo_url,
                    "address": hospital.address,
                    "availability": {
                        "start": start_time.strftime("%H:%M"),
                        "end": end_time.strftime("%H:%M")
                    },
                    "emergency_services_available": hospital.emergency_services_available
                })

            # Format doctor data with hospital list
            doctors_with_hospitals.append({
                "doctor_id": doctor.doctor_id,
                "title": doctor.title,
                "name": doctor.name,
                "specialization": doctor.specialization,
                "profile_picture_url": doctor.profile_picture_url,
                "created_at": doctor.created_at,
                "updated_at": doctor.updated_at,
                "hospitals": hospital_list
            })

        return doctors_with_hospitals

    except Exception as e:
        logger.error(f"Error fetching doctors with hospitals: {str(e)}")
        raise HTTPException(status_code=500, detail="Could not fetch doctors with hospitals")

@router.get("/all", response_model=List[DoctorResponse])
async def get_all_doctors(
    specialization: Optional[str] = Query(None, description="Filter doctors by specialization"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    _: dict = Depends(JWTBearer())
):
    """
    Retrieve all doctors with optional filtering by specialization.
    """
    try:
        query = db.query(Doctor)
        
        if specialization:
            query = query.filter(Doctor.specialization == specialization)
        
        doctors = query.offset(skip).limit(limit).all()
        return doctors
    except SQLAlchemyError as e:
        logger.error(f"Database error retrieving doctors: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not retrieve doctors"
        )

@router.get("/{doctor_id}", response_model=DoctorResponse)
async def get_doctor(
    doctor_id: int,
    db: Session = Depends(get_db),
    _: dict = Depends(JWTBearer())
):
    """
    Retrieve a specific doctor by ID.
    """
    try:
        doctor = db.query(Doctor).filter(Doctor.doctor_id == doctor_id).first()
        if not doctor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Doctor with ID {doctor_id} not found"
            )
        return doctor
    except SQLAlchemyError as e:
        logger.error(f"Database error retrieving doctor: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not retrieve doctor"
        )


@router.put("/{doctor_id}", response_model=DoctorResponse)
async def update_doctor(
    doctor_id: int,
    doctor_update: DoctorUpdate,
    current_user: dict = Depends(JWTBearer()),
    db: Session = Depends(get_db)
):
    """
    Update a doctor's information. Only admin users can update doctor records.
    """
    try:
        if current_user.get("role") != "Admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only administrators can update doctor records"
            )

        doctor = db.query(Doctor).filter(Doctor.doctor_id == doctor_id).first()
        if not doctor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Doctor with ID {doctor_id} not found"
            )

        update_data = doctor_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(doctor, field, value)

        db.commit()
        db.refresh(doctor)
        logger.info(f"Updated doctor record for ID {doctor_id}")
        return doctor
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error updating doctor: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not update doctor record"
        )

@router.delete("/{doctor_id}")
async def delete_doctor(
    doctor_id: int,
    current_user: dict = Depends(JWTBearer()),
    db: Session = Depends(get_db)
):
    """
    Delete a doctor record. Only admin users can delete doctor records.
    """
    try:
        if current_user.get("role") != "Admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only administrators can delete doctor records"
            )

        doctor = db.query(Doctor).filter(Doctor.doctor_id == doctor_id).first()
        if not doctor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Doctor with ID {doctor_id} not found"
            )

        db.delete(doctor)
        db.commit()
        logger.info(f"Deleted doctor record for ID {doctor_id}")
        return {"message": "Doctor deleted successfully"}
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error deleting doctor: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not delete doctor record"
        )

@router.get("/search/", response_model=List[DoctorResponse])
async def search_doctors(
    query: Optional[str] = Query(None, description="General search query"),
    doctor_name: Optional[str] = Query(None, description="Search by doctor name"),
    hospital_name: Optional[str] = Query(None, description="Search by hospital name"),
    specialization: Optional[str] = Query(None, description="Filter by specialization"),
    hospital_id: Optional[int] = Query(None, description="Filter by hospital ID"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Search for doctors with multiple filter options.
    """
    try:
        # Validate hospital_id
        if hospital_id and not isinstance(hospital_id, int):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="hospital_id must be an integer"
            )

        # Start with base query
        base_query = db.query(Doctor).distinct()

        # Join with hospitals if we need to search by hospital name or hospital ID
        if hospital_name or hospital_id:
            base_query = base_query.join(HospitalDoctor).join(Hospital)

        # Apply filters
        filters = []

        # General search query
        if query:
            search_term = f"%{query.lower()}%"
            filters.append(
                or_(
                    func.lower(Doctor.name).ilike(search_term),
                    func.lower(Doctor.specialization).ilike(search_term),
                    func.lower(Doctor.title).ilike(search_term)
                )
            )

        # Specific doctor name search
        if doctor_name:
            doctor_search = f"%{doctor_name.lower()}%"
            filters.append(
                or_(
                    func.lower(Doctor.name).ilike(doctor_search),
                    func.lower(Doctor.title).ilike(doctor_search)
                )
            )

        # Hospital name search
        if hospital_name:
            hospital_search = f"%{hospital_name.lower()}%"
            filters.append(func.lower(Hospital.name).ilike(hospital_search))

        # Specialization filter
        if specialization:
            filters.append(Doctor.specialization == specialization)

        # Hospital ID filter
        if hospital_id:
            filters.append(HospitalDoctor.hospitalID == hospital_id)

        # Apply all filters
        if filters:
            base_query = base_query.filter(and_(*filters))

        # Apply pagination
        doctors = base_query.offset(skip).limit(limit).all()

        # Format response with hospitals and availability
        doctors_with_details = []
        for doctor in doctors:
            # Get associated hospitals with availability
            hospitals_data = db.query(
                Hospital,
                HospitalDoctor.availability_start_time,
                HospitalDoctor.availability_end_time
            ).join(
                HospitalDoctor,
                Hospital.hospital_id == HospitalDoctor.hospitalID
            ).filter(
                HospitalDoctor.doctorID == doctor.doctor_id
            ).all()

            # Format hospital list
            hospital_list = []
            for hospital, start_time, end_time in hospitals_data:
                hospital_list.append({
                    "hospital_id": hospital.hospital_id,
                    "name": hospital.name,
                    "logo_url": hospital.logo_url,
                    "address": hospital.address,
                    "availability": {
                        "start": start_time.strftime("%H:%M"),
                        "end": end_time.strftime("%H:%M")
                    },
                    "emergency_services_available": hospital.emergency_services_available
                })

            doctors_with_details.append({
                "doctor_id": doctor.doctor_id,
                "title": doctor.title,
                "name": doctor.name,
                "specialization": doctor.specialization,
                "profile_picture_url": doctor.profile_picture_url,
                "created_at": doctor.created_at,
                "updated_at": doctor.updated_at,
                "hospitals": hospital_list
            })

        return doctors_with_details

    except SQLAlchemyError as e:
        logger.error(f"Database error searching doctors: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not search doctors"
        )
    
