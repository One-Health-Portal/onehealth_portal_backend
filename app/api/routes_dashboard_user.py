from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from typing import List
from app.db.connection import get_db
from app.models.user import User
from app.schemas.user_schema import UserResponse, UserCreate, UserUpdateDashBoard
from app.core.jwt_auth import JWTBearer
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/users", response_model=List[UserResponse])
async def get_users(
    current_user: User = Depends(JWTBearer()),
    db: Session = Depends(get_db)
):
    """
    Fetch all users from the database for the dashboard.
    """
    try:
        users = db.query(User).all()
        return users
    except Exception as e:
        logger.error(f"Error fetching users: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An error occurred while fetching users"
        )

@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdateDashBoard,
    current_user: User = Depends(JWTBearer()),
    db: Session = Depends(get_db)
):
    """
    Update an existing user in the database.
    """
    try:
        # Fetch the user by ID
        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )

        # Ensure only Admins or Staff can update users
        if current_user.role not in ["Admin", "Staff"]:
            raise HTTPException(
                status_code=403,
                detail="Not authorized to update users"
            )

        # Update user fields if provided
        if user_data.title:
            user.title = user_data.title
        if user_data.first_name:
            user.first_name = user_data.first_name
        if user_data.last_name:
            user.last_name = user_data.last_name
        if user_data.email:
            user.email = user_data.email
        if user_data.phone:
            user.phone = user_data.phone
        if user_data.role:
            user.role = user_data.role

        db.commit()
        db.refresh(user)
        return user
    except HTTPException as http_error:
        raise http_error
    except Exception as e:
        logger.error(f"Error updating user: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An error occurred while updating the user"
        )

@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    current_user: User = Depends(JWTBearer()),
    db: Session = Depends(get_db)
):
    """
    Delete a user from the database.
    """
    try:
        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )

        db.delete(user)
        db.commit()
        return {"message": "User deleted successfully"}
    except HTTPException as http_error:
        raise http_error
    except Exception as e:
        logger.error(f"Error deleting user: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An error occurred while deleting the user"
        )