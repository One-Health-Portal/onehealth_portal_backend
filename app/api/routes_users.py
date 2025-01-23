from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List
from app.db.connection import get_db
from app.models.user import User
from app.schemas.user_schema import UserCreate, UserUpdate, UserResponse
from app.core.jwt_auth import JWTBearer
import hashlib
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/profile", response_model=UserResponse)
async def get_user_profile(
    current_user: User = Depends(JWTBearer()),
    db: Session = Depends(get_db)
):
    """
    Retrieve the profile of the currently authenticated user.
    """
    try:
        user = db.query(User).filter(User.supabase_uid == current_user.supabase_uid).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Database error occurred")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="An unexpected error occurred")

@router.put("/profile", response_model=UserResponse)
async def update_profile(
    user_update: UserUpdate,
    current_user: User = Depends(JWTBearer()),
    db: Session = Depends(get_db)
):
    """
    Update the profile information of the currently authenticated user.
    """
    try:
        user = db.query(User).filter(User.email == current_user.email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        for field, value in user_update.model_dump(exclude_unset=True).items():
            setattr(user, field, value)
        db.commit()
        db.refresh(user)
        return user
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error occurred")

@router.get("/all", response_model=List[UserResponse])
async def get_all_users(
    current_user: dict = Depends(JWTBearer()),
    db: Session = Depends(get_db)
):
    """
    Retrieve a list of all users. Only accessible by Admin users.
    """
    if current_user.get("role") != "Admin":
        raise HTTPException(status_code=403, detail="Not authorized to view all users")
    try:
        users = db.query(User).all()
        return users
    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error occurred")