from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Optional
from datetime import datetime, time, timedelta, date
import logging

from app.db.connection import get_db
from app.models.lab_test import LabTest
from app.models.hospital import Hospital
from app.schemas.lab_test_schema import (
    LabTestCreate,
    LabTestUpdate,
    LabTestResponse,
    TimeSlotResponse,
    LabTestAvailabilityResponse,
)
from app.core.jwt_auth import JWTBearer
from app.models.user import User  # Import the User model

logger = logging.getLogger(__name__)
router = APIRouter()

# Helper function to generate time slots
# Helper function to generate time slots
def generate_time_slots(start_time: time, end_time: time) -> List[TimeSlotResponse]:
    """
    Generate time slots between start and end times.
    """
    slots = []
    current_datetime = datetime.combine(datetime.today(), start_time)
    end_datetime = datetime.combine(datetime.today(), end_time)

    while current_datetime < end_datetime:
        slots.append({
            "time": current_datetime.strftime("%I:%M %p"),
            "available": True
        })
        current_datetime += timedelta(minutes=30)  # 30-minute slots

    return slots

# Endpoint to get lab test availability
@router.get("/{hospital_id}/availability", response_model=LabTestAvailabilityResponse)
async def get_lab_test_availability(
    hospital_id: int,
    selected_date: Optional[date] = None,
    db: Session = Depends(get_db)
):
    """
    Retrieve lab test availability for a specific hospital.
    """
    try:
        # Query the hospital to get operating hours
        hospital = db.query(Hospital).filter(Hospital.hospital_id == hospital_id).first()

        if not hospital:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Hospital not found."
            )

        # Default operating hours if not specified in the Hospital model
        start_time = time(9, 0)  # Default 9:00 AM
        end_time = time(17, 0)   # Default 5:00 PM

        # Generate time slots
        time_slots = generate_time_slots(start_time, end_time)

        # Check for existing lab tests on the selected date
        if selected_date:
            existing_lab_tests = db.query(LabTest).filter(
                LabTest.hospital_id == hospital_id,
                LabTest.test_date == selected_date
            ).all()

            # Mark slots as unavailable if already booked
            for lab_test in existing_lab_tests:
                for slot in time_slots:
                    if slot['time'] == lab_test.test_time.strftime("%I:%M %p"):
                        slot['available'] = False

        return {
            "hospital_id": hospital_id,
            "start_time": start_time,
            "end_time": end_time,
            "time_slots": time_slots,
            "available": True
        }

    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not retrieve lab test availability."
        )

# Existing endpoints
@router.get("/history", response_model=List[LabTestResponse])
async def get_lab_test_history(
    current_user: User = Depends(JWTBearer()),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 10
):
    """
    Retrieve lab test history for the current user.
    Admins and staff can view all lab tests, while regular users can only view their own.
    """
    try:
        query = db.query(LabTest).options(joinedload(LabTest.hospital))

        if current_user.role in ["Admin", "Staff"]:
            # Admins and staff can view all lab tests
            lab_tests = query.offset(skip).limit(limit).all()
        else:
            # Regular users can only view their own lab tests
            lab_tests = query.filter(LabTest.user_id == current_user.user_id).offset(skip).limit(limit).all()

        if not lab_tests:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No lab tests found for the current user."
            )

        # Map the results to include the hospital name
        lab_tests_response = [
            LabTestResponse(
                lab_test_id=lab_test.lab_test_id,
                user_id=lab_test.user_id,
                hospital_id=lab_test.hospital_id,
                hospital_name=lab_test.hospital.name,  # Include hospital name
                test_type=lab_test.test_type,
                test_date=lab_test.test_date,
                test_time=lab_test.test_time.strftime("%I:%M %p"),  # Format time as "HH:MM AM/PM"
                status=lab_test.status,
                result=lab_test.result,
                instruction=lab_test.instruction,
                created_at=lab_test.created_at,
                updated_at=lab_test.updated_at,
            )
            for lab_test in lab_tests
        ]

        return lab_tests_response
    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not retrieve lab test history."
        )

@router.post("/", response_model=LabTestResponse)
async def create_lab_test(
    lab_test: LabTestCreate,
    current_user: User = Depends(JWTBearer()),
    db: Session = Depends(get_db)
):
    """
    Create a new lab test.
    Admins and staff can create lab tests for any user, while regular users can only create lab tests for themselves.
    """
    try:
        # Log the incoming request payload for debugging
        logger.info(f"Received lab test creation request: {lab_test.model_dump()}")

        # Authorization check
        if current_user.role not in ["Admin", "Staff"] and lab_test.user_id != current_user.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to create lab test for other users."
            )

        # Validate the hospital exists
        hospital = db.query(Hospital).filter(Hospital.hospital_id == lab_test.hospital_id).first()
        if not hospital:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Hospital with ID {lab_test.hospital_id} not found."
            )

        # Validate the selected date and time
        if lab_test.test_date < date.today():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Test date cannot be in the past."
            )

        # Check if the selected time slot is available
        existing_lab_test = db.query(LabTest).filter(
            LabTest.hospital_id == lab_test.hospital_id,
            LabTest.test_date == lab_test.test_date,
            LabTest.test_time == lab_test.test_time
        ).first()

        if existing_lab_test:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The selected time slot is already booked."
            )

        # Create the new lab test
        new_lab_test = LabTest(
            user_id=lab_test.user_id,
            hospital_id=lab_test.hospital_id,
            test_type=lab_test.test_type,
            test_date=lab_test.test_date,
            test_time=lab_test.test_time,  # This is now a time object
            status="Scheduled",  # Default status
            result=None,  # Default result
            instruction=lab_test.instruction,
        )

        db.add(new_lab_test)
        db.commit()
        db.refresh(new_lab_test)

        # Log successful creation
        logger.info(f"Lab test created successfully: {new_lab_test}")

        return new_lab_test

    except HTTPException as e:
        # Re-raise HTTPException to return the error response
        raise e

    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not create lab test due to a database error."
        )

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while creating the lab test."
        )

@router.get("/all", response_model=List[LabTestResponse])
async def get_all_lab_tests(
    current_user: User = Depends(JWTBearer()),
    db: Session = Depends(get_db)
):
    """
    Retrieve all lab tests.
    Admins and staff can view all lab tests, while regular users can only view their own.
    """
    try:
        if current_user.role in ["Admin", "Staff"]:
            lab_tests = db.query(LabTest).all()
        else:
            lab_tests = db.query(LabTest).filter(
                LabTest.user_id == current_user.user_id  # Use user_id instead of id
            ).all()

        return lab_tests
    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not retrieve lab tests."
        )

@router.get("/{lab_test_id}", response_model=LabTestResponse)
async def get_lab_test(
    lab_test_id: int,
    current_user: User = Depends(JWTBearer()),
    db: Session = Depends(get_db)
):
    """
    Retrieve a specific lab test by ID.
    Admins and staff can view any lab test, while regular users can only view their own.
    """
    try:
        lab_test = db.query(LabTest).filter(LabTest.lab_test_id == lab_test_id).first()
        if not lab_test:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lab test not found."
            )

        if current_user.role not in ["Admin", "Staff"] and lab_test.user_id != current_user.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view this lab test."
            )

        return lab_test
    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not retrieve lab test."
        )

@router.put("/{lab_test_id}", response_model=LabTestResponse)
async def update_lab_test(
    lab_test_id: int,
    lab_test_update: LabTestUpdate,
    current_user: User = Depends(JWTBearer()),
    db: Session = Depends(get_db)
):
    """
    Update a specific lab test by ID.
    Admins and staff can update any lab test, while regular users can only update their own.
    """
    try:
        lab_test = db.query(LabTest).filter(LabTest.lab_test_id == lab_test_id).first()
        if not lab_test:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lab test not found."
            )

        if current_user.role not in ["Admin", "Staff"] and lab_test.user_id != current_user.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this lab test."
            )

        for field, value in lab_test_update.model_dump(exclude_unset=True).items():
            setattr(lab_test, field, value)

        db.commit()
        db.refresh(lab_test)
        return lab_test
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not update lab test."
        )

# Endpoint to cancel a lab test
@router.delete("/{lab_test_id}")
async def cancel_lab_test(
    lab_test_id: int,
    current_user: User = Depends(JWTBearer()),
    db: Session = Depends(get_db)
):
    """
    Cancel a specific lab test by ID.
    Admins and staff can cancel any lab test, while regular users can only cancel their own.
    """
    try:
        lab_test = db.query(LabTest).filter(LabTest.lab_test_id == lab_test_id).first()
        if not lab_test:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lab test not found."
            )

        # Authorization check
        if current_user.role not in ["Admin", "Staff"] and lab_test.user_id != current_user.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to cancel this lab test."
            )

        # Update the status to "Cancelled"
        lab_test.status = "Cancelled"
        db.commit()

        return {"message": "Lab test cancelled successfully."}
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not cancel lab test."
        )

@router.post("/book", response_model=LabTestResponse)
async def book_lab_test(
    lab_test: LabTestCreate,
    current_user: User = Depends(JWTBearer()),
    db: Session = Depends(get_db)
):
    try:
        # Validate the hospital
        hospital = db.query(Hospital).filter(Hospital.hospital_id == lab_test.hospital_id).first()
        if not hospital:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Hospital with ID {lab_test.hospital_id} not found."
            )

        # Create lab test
        new_lab_test = LabTest(
            user_id=lab_test.user_id,
            hospital_id=lab_test.hospital_id,
            test_type=lab_test.test_type,
            test_date=lab_test.test_date,
            test_time=lab_test.test_time,  # Already a time object
            status="Scheduled",
            instruction=lab_test.instruction,
        )
        
        db.add(new_lab_test)
        db.commit()
        db.refresh(new_lab_test)

        # Prepare the response
        response = LabTestResponse(
            lab_test_id=new_lab_test.lab_test_id,
            user_id=new_lab_test.user_id,
            hospital_id=new_lab_test.hospital_id,
            hospital_name=hospital.name,  # Include hospital name
            test_type=new_lab_test.test_type,
            test_date=new_lab_test.test_date,
            test_time=new_lab_test.test_time,  # Will be formatted as "HH:MM AM/PM"
            status=new_lab_test.status,
            result=new_lab_test.result,
            instruction=new_lab_test.instruction,
            created_at=new_lab_test.created_at,
            updated_at=new_lab_test.updated_at,
        )

        return response

    except HTTPException as e:
        raise e
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not create lab test booking."
        )
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while processing the booking."
        )