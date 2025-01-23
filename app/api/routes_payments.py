# routes_payments.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List
from app.db.connection import get_db
from app.models.payment import Payment
from app.models.appointment import Appointment
from app.models.user import User
from app.schemas.payment_schema import PaymentCreate, PaymentUpdate, PaymentResponse
from app.core.jwt_auth import JWTBearer
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/", response_model=PaymentResponse)
async def create_payment(
    payment: PaymentCreate,
    current_user: User = Depends(JWTBearer()),
    db: Session = Depends(get_db)
):
    try:
        # Verify appointment exists and belongs to user
        appointment = db.query(Appointment).filter(
            Appointment.appointment_id == payment.appointment_id
        ).first()
        
        if not appointment:
            raise HTTPException(status_code=404, detail="Appointment not found")

        new_payment = Payment(**payment.model_dump())
        db.add(new_payment)
        db.commit()
        db.refresh(new_payment)
        return new_payment
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Could not create payment")

@router.get("/all", response_model=List[PaymentResponse])
async def get_all_payments(
    current_user: dict = Depends(JWTBearer()),
    db: Session = Depends(get_db)
):
    try:
        if current_user.get("role") in ["Admin", "Staff"]:
            payments = db.query(Payment).all()
        else:
            # Get payments for user's appointments
            payments = db.query(Payment).join(
                Appointment, Payment.appointment_id == Appointment.appointment_id
            ).filter(Appointment.user_id == current_user.get("id")).all()
        return payments
    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Could not retrieve payments")

@router.get("/{payment_id}", response_model=PaymentResponse)
async def get_payment(
    payment_id: int,
    current_user: dict = Depends(JWTBearer()),
    db: Session = Depends(get_db)
):
    try:
        payment = db.query(Payment).filter(Payment.payment_id == payment_id).first()
        if not payment:
            raise HTTPException(status_code=404, detail="Payment not found")
        
        # Check authorization
        appointment = db.query(Appointment).filter(
            Appointment.appointment_id == payment.appointment_id
        ).first()
        
        if current_user.get("role") not in ["Admin", "Staff"] and appointment.user_id != current_user.get("id"):
            raise HTTPException(status_code=403, detail="Not authorized to view this payment")
        
        return payment
    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Could not retrieve payment")

@router.put("/{payment_id}", response_model=PaymentResponse)
async def update_payment(
    payment_id: int,
    payment_update: PaymentUpdate,
    current_user: dict = Depends(JWTBearer()),
    db: Session = Depends(get_db)
):
    try:
        payment = db.query(Payment).filter(Payment.payment_id == payment_id).first()
        if not payment:
            raise HTTPException(status_code=404, detail="Payment not found")
        
        # Only admin/staff can update payments
        if current_user.get("role") not in ["Admin", "Staff"]:
            raise HTTPException(status_code=403, detail="Not authorized to update payments")
        
        for field, value in payment_update.model_dump(exclude_unset=True).items():
            setattr(payment, field, value)
        
        db.commit()
        db.refresh(payment)
        return payment
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Could not update payment")

@router.delete("/{payment_id}")
async def delete_payment(
    payment_id: int,
    current_user: dict = Depends(JWTBearer()),
    db: Session = Depends(get_db)
):
    try:
        payment = db.query(Payment).filter(Payment.payment_id == payment_id).first()
        if not payment:
            raise HTTPException(status_code=404, detail="Payment not found")
        
        # Only admin/staff can delete payments
        if current_user.get("role") not in ["Admin", "Staff"]:
            raise HTTPException(status_code=403, detail="Not authorized to delete payments")
        
        db.delete(payment)
        db.commit()
        return {"message": "Payment deleted successfully"}
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Could not delete payment")
