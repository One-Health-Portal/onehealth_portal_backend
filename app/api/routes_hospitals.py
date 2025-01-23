# routes_hospitals.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List
from app.db.connection import get_db
from app.models.hospital import Hospital
from app.schemas.hospital_schema import HospitalCreate, HospitalUpdate, HospitalResponse
from app.core.jwt_auth import JWTBearer
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/", response_model=HospitalResponse)
async def create_hospital(
    hospital: HospitalCreate,
    current_user: dict = Depends(JWTBearer()),
    db: Session = Depends(get_db)
):
    try:
        if current_user.get("role") not in ["Admin"]:
            raise HTTPException(
                status_code=403,
                detail="Only administrators can create hospitals"
            )
        
        new_hospital = Hospital(**hospital.model_dump())
        db.add(new_hospital)
        db.commit()
        db.refresh(new_hospital)
        return new_hospital
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Could not create hospital")

@router.get("/all", response_model=List[HospitalResponse])
async def get_all_hospitals(
    current_user: dict = Depends(JWTBearer()),
    db: Session = Depends(get_db)
):
    try:
        hospitals = db.query(Hospital).all()
        return hospitals
    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Could not retrieve hospitals")

@router.get("/{hospital_id}", response_model=HospitalResponse)
async def get_hospital(
    hospital_id: int,
    db: Session = Depends(get_db)
):
    try:
        hospital = db.query(Hospital).filter(Hospital.hospital_id == hospital_id).first()
        if not hospital:
            raise HTTPException(status_code=404, detail="Hospital not found")
        return hospital
    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Could not retrieve hospital")

@router.put("/{hospital_id}", response_model=HospitalResponse)
async def update_hospital(
    hospital_id: int,
    hospital_update: HospitalUpdate,
    current_user: dict = Depends(JWTBearer()),
    db: Session = Depends(get_db)
):
    try:
        if current_user.get("role") not in ["Admin"]:
            raise HTTPException(
                status_code=403,
                detail="Only administrators can update hospitals"
            )
        
        hospital = db.query(Hospital).filter(Hospital.hospital_id == hospital_id).first()
        if not hospital:
            raise HTTPException(status_code=404, detail="Hospital not found")
        
        for field, value in hospital_update.model_dump(exclude_unset=True).items():
            setattr(hospital, field, value)
        
        db.commit()
        db.refresh(hospital)
        return hospital
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Could not update hospital")

@router.delete("/{hospital_id}")
async def delete_hospital(
    hospital_id: int,
    current_user: dict = Depends(JWTBearer()),
    db: Session = Depends(get_db)
):
    try:
        if current_user.get("role") not in ["Admin"]:
            raise HTTPException(
                status_code=403,
                detail="Only administrators can delete hospitals"
            )
        
        hospital = db.query(Hospital).filter(Hospital.hospital_id == hospital_id).first()
        if not hospital:
            raise HTTPException(status_code=404, detail="Hospital not found")
        
        db.delete(hospital)
        db.commit()
        return {"message": "Hospital deleted successfully"}
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Could not delete hospital")