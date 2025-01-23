from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List
from app.db.connection import get_db
from app.models.feedback import Feedback
from app.models.appointment import Appointment
from app.schemas.feedback_schema import FeedbackCreate, FeedbackUpdate, FeedbackResponse
from app.core.jwt_auth import JWTBearer
from app.models.user import UserPayload  # Import UserPayload from the correct location
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/", response_model=FeedbackResponse)
async def create_feedback(
    feedback: FeedbackCreate,
    current_user: UserPayload = Depends(JWTBearer()),  # Use UserPayload here
    db: Session = Depends(get_db)
):
    try:
        # Verify if the appointment exists and belongs to the user
        if feedback.appointment_id:
            appointment = db.query(Appointment).filter(
                Appointment.appointment_id == feedback.appointment_id
            ).first()
            if not appointment:
                raise HTTPException(status_code=404, detail="Appointment not found")
            if appointment.user_id != current_user.user_id:  # Use current_user.user_id
                raise HTTPException(status_code=403, detail="Feedback can only be given for your own appointments")

        # Verify the user is giving feedback for themselves
        if current_user.role not in ["Admin", "Staff"] and feedback.user_id != current_user.user_id:  # Use current_user.user_id
            raise HTTPException(status_code=403, detail="You can only submit feedback for yourself")

        new_feedback = Feedback(**feedback.model_dump())
        db.add(new_feedback)
        db.commit()
        db.refresh(new_feedback)
        return new_feedback
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Could not create feedback")

@router.get("/all", response_model=List[FeedbackResponse])
async def get_all_feedback(
    current_user: UserPayload = Depends(JWTBearer()),  # Use UserPayload here
    db: Session = Depends(get_db)
):
    try:
       
        feedback = db.query(Feedback).filter(
            Feedback.user_id == current_user.user_id  # Access user_id directly
        ).all()
        return feedback
    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Could not retrieve feedback")

@router.get("/{feedback_id}", response_model=FeedbackResponse)
async def get_feedback(
    feedback_id: int,
    current_user: UserPayload = Depends(JWTBearer()),  # Use UserPayload here
    db: Session = Depends(get_db)
):
    try:
        feedback = db.query(Feedback).filter(Feedback.feedback_id == feedback_id).first()
        if not feedback:
            raise HTTPException(status_code=404, detail="Feedback not found")
        
        if current_user.role not in ["Admin", "Staff"] and feedback.user_id != current_user.user_id:  # Access user_id directly
            raise HTTPException(status_code=403, detail="Not authorized to view this feedback")
        
        return feedback
    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Could not retrieve feedback")

@router.put("/{feedback_id}", response_model=FeedbackResponse)
async def update_feedback(
    feedback_id: int,
    feedback_update: FeedbackUpdate,
    current_user: UserPayload = Depends(JWTBearer()),  # Use UserPayload here
    db: Session = Depends(get_db)
):
    try:
        feedback = db.query(Feedback).filter(Feedback.feedback_id == feedback_id).first()
        if not feedback:
            raise HTTPException(status_code=404, detail="Feedback not found")
        
        if current_user.role not in ["Admin", "Staff"] and feedback.user_id != current_user.user_id:  # Access user_id directly
            raise HTTPException(status_code=403, detail="Not authorized to update this feedback")
        
        for field, value in feedback_update.model_dump(exclude_unset=True).items():
            setattr(feedback, field, value)
        
        db.commit()
        db.refresh(feedback)
        return feedback
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Could not update feedback")

@router.delete("/{feedback_id}")
async def delete_feedback(
    feedback_id: int,
    current_user: UserPayload = Depends(JWTBearer()),  # Use UserPayload here
    db: Session = Depends(get_db)
):
    try:
        feedback = db.query(Feedback).filter(Feedback.feedback_id == feedback_id).first()
        if not feedback:
            raise HTTPException(status_code=404, detail="Feedback not found")
        
        if current_user.role not in ["Admin", "Staff"] and feedback.user_id != current_user.user_id:  # Access user_id directly
            raise HTTPException(status_code=403, detail="Not authorized to delete this feedback")
        
        db.delete(feedback)
        db.commit()
        return {"message": "Feedback deleted successfully"}
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Could not delete feedback")