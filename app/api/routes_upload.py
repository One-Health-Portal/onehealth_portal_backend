# app/api/routes_upload.py
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.db.connection import get_db
from app.core.jwt_auth import JWTBearer
from app.core.cloudinary_config import upload_image
from app.models.user import User
from app.models.doctor import Doctor
from app.models.hospital import Hospital
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/user/profile-picture")
async def upload_user_profile_picture(
    file: UploadFile = File(...),
    current_user: User = Depends(JWTBearer()),  # Note: This returns a User object, not dict
    db: Session = Depends(get_db)
):
    """Upload a user's profile picture to Cloudinary"""
    try:
        # Upload image to cloudinary
        image_url = await upload_image(file, "user_profiles")
        
        # Update user's profile picture URL in database
        # Access user_id directly from User object
        if not current_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        current_user.profile_picture_url = image_url
        db.commit()
        
        return {"message": "Profile picture uploaded successfully", "url": image_url}
    
    except Exception as e:
        logger.error(f"Error uploading profile picture: {str(e)}")
        db.rollback()  # Add rollback on error
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/doctor/profile-picture/{doctor_id}")
async def upload_doctor_profile_picture(
    doctor_id: int,
    file: UploadFile = File(...),
    current_user: dict = Depends(JWTBearer()),
    db: Session = Depends(get_db)
):
    """Upload a doctor's profile picture to Cloudinary"""
    try:
        # Verify admin access
        if current_user.get("role") != "Admin":
            raise HTTPException(
                status_code=403,
                detail="Only administrators can update doctor profile pictures"
            )
        
        # Upload image to cloudinary
        image_url = await upload_image(file, "doctor_profiles")
        
        # Update doctor's profile picture URL in database
        doctor = db.query(Doctor).filter(Doctor.doctor_id == doctor_id).first()
        if not doctor:
            raise HTTPException(status_code=404, detail="Doctor not found")
        
        doctor.profile_picture_url = image_url
        db.commit()
        
        return {"message": "Doctor profile picture uploaded successfully", "url": image_url}
    
    except Exception as e:
        logger.error(f"Error uploading doctor profile picture: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to upload doctor profile picture")

@router.post("/hospital/logo/{hospital_id}")
async def upload_hospital_logo(
    hospital_id: int,
    file: UploadFile = File(...),
    current_user: dict = Depends(JWTBearer()),
    db: Session = Depends(get_db)
):
    """Upload a hospital's logo to Cloudinary"""
    try:
        # Verify admin access
        if current_user.get("role") != "Admin":
            raise HTTPException(
                status_code=403,
                detail="Only administrators can update hospital logos"
            )
        
        # Upload image to cloudinary
        image_url = await upload_image(file, "hospital_logos")
        
        # Update hospital's logo URL in database
        hospital = db.query(Hospital).filter(Hospital.hospital_id == hospital_id).first()
        if not hospital:
            raise HTTPException(status_code=404, detail="Hospital not found")
        
        hospital.logo_url = image_url
        db.commit()
        
        return {"message": "Hospital logo uploaded successfully", "url": image_url}
    
    except Exception as e:
        logger.error(f"Error uploading hospital logo: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to upload hospital logo")