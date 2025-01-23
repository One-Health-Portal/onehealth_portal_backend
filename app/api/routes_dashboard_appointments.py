from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func
from typing import List, Optional, Tuple
from datetime import date, datetime, time, timedelta
from app.db.connection import get_db
from app.models.doctor import Doctor
from app.models.hospital import Hospital
from app.models.hospital_doctor import HospitalDoctor
from app.models.appointment import Appointment
from app.models.payment import Payment
from app.schemas.appointment_schema import (
    AvailableTimeSlotsResponse,
    DoctorHospitalsResponse,
    AppointmentCreateRequest,
    AppointmentResponse,
)
from app.core.jwt_auth import JWTBearer
from app.models.user import User
from app.services.pdf_service import PDFService
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

def format_appointments(appointments: List[Appointment]) -> List[dict]:
    """
    Format appointments for the response
    """
    formatted_appointments = []
    for appointment in appointments:
        formatted_appointment = {
            "appointment_id": appointment.appointment_id,
            "user_id": appointment.user_id,
            "doctor_id": appointment.doctor_id,
            "hospital_id": appointment.hospital_id,
            "appointment_date": appointment.appointment_date.date(),
            "appointment_time": appointment.appointment_time.strftime("%I:%M %p"),
            "status": appointment.status,
            "note": appointment.note,
            "appointment_number": appointment.appointment_number,
            "created_at": appointment.created_at,
            "updated_at": appointment.updated_at,
            "payment_status": appointment.payment.payment_status if appointment.payment else None,
            "total_amount": float(appointment.payment.amount) if appointment.payment else 0.0,
            "doctor_name": f"{appointment.doctor.title} {appointment.doctor.name}" if appointment.doctor else None,
            "doctor_specialization": appointment.doctor.specialization if appointment.doctor else None,
            "hospital_name": appointment.hospital.name if appointment.hospital else None,
            "user_name": f"{appointment.user.first_name} {appointment.user.last_name}" if appointment.user else None,  # Added user's full name
            "user_email": appointment.user.email if appointment.user else None,
            "user_phone": appointment.user.phone if appointment.user else None
        }
        formatted_appointments.append(formatted_appointment)
    return formatted_appointments

def calculate_detailed_time_slots(
    start_time: time,
    end_time: time,
    appointments: List[Appointment],
    selected_date: date
) -> Tuple[List[dict], List[dict]]:
    """
    Calculate available and unavailable time slots for a specific date
    """
    start_datetime = datetime.combine(selected_date, start_time)
    end_datetime = datetime.combine(selected_date, end_time)
    current_datetime = datetime.now()
    
    available_slots = []
    unavailable_slots = []

    # Create a mapping of booked appointments
    booked_slots = {}
    for appointment in appointments:
        time_key = appointment.appointment_time.strftime("%H:%M:%S")
        booked_slots[time_key] = {
            "appointment_number": appointment.appointment_number,
            "status": appointment.status,
            "note": appointment.note
        }

    # Generate all possible 30-minute slots
    current_time = start_datetime
    while current_time < end_datetime:
        slot_time = current_time.time()
        slot_time_str = slot_time.strftime("%H:%M:%S")
        formatted_time = slot_time.strftime("%I:%M %p")
        
        # Check if slot is in the past
        if selected_date == current_datetime.date() and current_time <= current_datetime:
            unavailable_slots.append({
                "time": formatted_time,
                "available": False
            })
        
        # Check if slot is booked
        elif slot_time_str in booked_slots:
            unavailable_slots.append({
                "time": formatted_time,
                "available": False
            })
        
        # Slot is available
        else:
            available_slots.append({
                "time": formatted_time,
                "available": True
            })

        current_time += timedelta(minutes=30)

    return available_slots, unavailable_slots

@router.get("/all", response_model=List[AppointmentResponse])
async def get_all_appointments(
    status: Optional[str] = None,
    doctor_id: Optional[int] = None,
    hospital_id: Optional[int] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    current_user: User = Depends(JWTBearer()),
    db: Session = Depends(get_db)
):
    """
    Retrieve all appointments with optional filtering.
    Only accessible by Admin and Staff users.
    """
    try:
        # Check if user has permission to view all appointments
        if current_user.role not in ["Admin", "Staff"]:
            raise HTTPException(
                status_code=403,
                detail="Not authorized to view all appointments"
            )

        # Build base query
        query = (
            db.query(Appointment)
            .options(
                joinedload(Appointment.doctor),
                joinedload(Appointment.hospital),
                joinedload(Appointment.payment),
                joinedload(Appointment.user)  # Ensure the User relationship is loaded
            )
        )

        # Apply filters
        if status:
            query = query.filter(Appointment.status == status)
        if doctor_id:
            query = query.filter(Appointment.doctor_id == doctor_id)
        if hospital_id:
            query = query.filter(Appointment.hospital_id == hospital_id)
        if start_date:
            query = query.filter(func.date(Appointment.appointment_date) >= start_date)
        if end_date:
            query = query.filter(func.date(Appointment.appointment_date) <= end_date)

        # Order by date and time
        query = query.order_by(
            Appointment.appointment_date.desc(),
            Appointment.appointment_time.desc()
        )

        appointments = query.all()
        
        if not appointments:
            return []

        return [AppointmentResponse(**appt) for appt in format_appointments(appointments)]

    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Could not retrieve appointments")
    
@router.get("/doctors/{doctor_id}/appointments", response_model=AvailableTimeSlotsResponse)
async def get_doctor_appointments(
    doctor_id: int,
    hospital_id: int,
    selected_date: date,
    current_user: User = Depends(JWTBearer()),
    db: Session = Depends(get_db)
):
    """
    Retrieve appointments and available time slots for a specific doctor.
    Regular users can only see their own appointments.
    """
    try:
        # Check doctor availability
        availability = (
            db.query(HospitalDoctor)
            .filter(
                HospitalDoctor.doctorID == doctor_id,
                HospitalDoctor.hospitalID == hospital_id
            )
            .first()
        )

        if not availability:
            raise HTTPException(status_code=404, detail="Doctor availability not found")

        # Build appointment query
        appointments_query = (
            db.query(Appointment)
            .options(
                joinedload(Appointment.user),
                joinedload(Appointment.hospital),
                joinedload(Appointment.doctor),
                joinedload(Appointment.payment)
            )
            .filter(
                Appointment.doctor_id == doctor_id,
                Appointment.hospital_id == hospital_id,
                func.date(Appointment.appointment_date) == selected_date
            )
        )

        # Filter for regular users
        if current_user.role not in ["Admin", "Staff"]:
            appointments_query = appointments_query.filter(Appointment.user_id == current_user.user_id)

        appointments = appointments_query.all()

        # Calculate slots
        available_slots, unavailable_slots = calculate_detailed_time_slots(
            availability.availability_start_time,
            availability.availability_end_time,
            appointments,
            selected_date
        )

        return {
            "available_slots": available_slots,
            "unavailable_slots": unavailable_slots,
            "appointments": format_appointments(appointments)
        }

    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Could not retrieve appointments")

@router.post("/book")
async def create_appointment(
    appointment_data: AppointmentCreateRequest,
    current_user: User = Depends(JWTBearer()),
    db: Session = Depends(get_db)
):
    """
    Create a new appointment.
    Admin/Staff can book for any user, regular users can only book for themselves.
    """
    try:
        # Authorization check
        if current_user.role not in ["Admin", "Staff"] and appointment_data.user_id != current_user.user_id:
            raise HTTPException(
                status_code=403,
                detail="Not authorized to book appointments for other users"
            )

        # Generate appointment number
        last_appointment = db.query(Appointment).order_by(Appointment.appointment_id.desc()).first()
        new_number = int(last_appointment.appointment_number.split("-")[-1]) + 1 if last_appointment else 1
        appointment_number = f"APPT-NO-{new_number}"

        # Parse appointment time
        try:
            appointment_time = datetime.strptime(appointment_data.appointment_time, "%I:%M %p").time()
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid time format. Use 'HH:MM AM/PM'."
            )

        # Check for existing appointment
        existing_appointment = (
            db.query(Appointment)
            .filter(
                Appointment.doctor_id == appointment_data.doctor_id,
                Appointment.hospital_id == appointment_data.hospital_id,
                Appointment.appointment_date == appointment_data.appointment_date,
                Appointment.appointment_time == appointment_time
            )
            .first()
        )

        if existing_appointment:
            raise HTTPException(
                status_code=400,
                detail="Selected time slot is already booked"
            )

        # Create appointment
        new_appointment = Appointment(
            user_id=appointment_data.user_id if current_user.role in ["Admin", "Staff"] else current_user.user_id,
            doctor_id=appointment_data.doctor_id,
            hospital_id=appointment_data.hospital_id,
            appointment_date=appointment_data.appointment_date,
            appointment_time=appointment_time,
            status='Pending',
            appointment_number=appointment_number,
            note=appointment_data.note,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        db.add(new_appointment)
        db.commit()
        db.refresh(new_appointment)

        return {
            "message": "Appointment booked successfully",
            "appointment_number": appointment_number,
            "appointment_id": new_appointment.appointment_id
        }

    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Could not book appointment")

@router.get("/history", response_model=List[AppointmentResponse])
async def get_appointment_history(
    user_id: Optional[int] = None,
    current_user: User = Depends(JWTBearer()),
    db: Session = Depends(get_db)
):
    """
    Get appointment history.
    Admin/Staff can view any user's history, regular users can only view their own.
    """
    try:
        # Authorization check for specific user history
        if user_id and current_user.role not in ["Admin", "Staff"] and user_id != current_user.user_id:
            raise HTTPException(
                status_code=403,
                detail="Not authorized to view other users' appointments"
            )

        # Build query
        query = (
            db.query(Appointment)
            .options(
                joinedload(Appointment.doctor),
                joinedload(Appointment.hospital),
                joinedload(Appointment.payment),
                joinedload(Appointment.user)
            )
        )

        # Apply user filter based on role
        if current_user.role in ["Admin", "Staff"]:
            if user_id:
                query = query.filter(Appointment.user_id == user_id)
        else:
            query = query.filter(Appointment.user_id == current_user.user_id)

        appointments = query.order_by(
            Appointment.appointment_date.desc(),
            Appointment.appointment_time.desc()
        ).all()

        if not appointments:
            return []

        return [AppointmentResponse(**appt) for appt in format_appointments(appointments)]

    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Could not retrieve appointment history")

@router.get("/{appointment_id}/receipt")
async def get_appointment_receipt(
    appointment_id: int,
    current_user: User = Depends(JWTBearer()),
    db: Session = Depends(get_db)
):
    """
    Generate and return a PDF receipt for an appointment.
    Admin/Staff can access any receipt, regular users can only access their own.
    """
    try:
        appointment = (
            db.query(Appointment)
            .options(
                joinedload(Appointment.doctor),
                joinedload(Appointment.hospital),
                joinedload(Appointment.payment),
                joinedload(Appointment.user)
            )
            .filter(Appointment.appointment_id == appointment_id)
            .first()
        )

        if not appointment:
            raise HTTPException(status_code=404, detail="Appointment not found")

        # Authorization check
        if current_user.role not in ["Admin", "Staff"] and appointment.user_id != current_user.user_id:
            raise HTTPException(status_code=403, detail="Not authorized to view this receipt")

        # Convert dates and times
        def convert_to_date(date_obj):
            if isinstance(date_obj, datetime):
                return date_obj.date()
            elif isinstance(date_obj, date):
                return date_obj
            elif isinstance(date_obj, str):
                date_formats = ["%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%d-%m-%Y", "%m-%d-%Y"]
                for fmt in date_formats:
                    try:
                        return datetime.strptime(date_obj, fmt).date()
                    except ValueError:
                        continue
                raise ValueError(f"Unable to parse date: {date_obj}")
            else:
                raise ValueError(f"Unsupported date type: {type(date_obj)}")

        def convert_to_time(time_obj):
            if isinstance(time_obj, datetime):
                return time_obj.time()
            elif isinstance(time_obj, time):
                return time_obj
            elif isinstance(time_obj, str):
                time_formats = [
                    "%H:%M:%S",
                    "%H:%M",
                    "%I:%M %p",
                    "%I:%M:%S %p"
                ]
                for fmt in time_formats:
                    try:
                        return datetime.strptime(time_obj, fmt).time()
                    except ValueError:
                        continue
                raise ValueError(f"Unable to parse time: {time_obj}")
            else:
                raise ValueError(f"Unsupported time type: {type(time_obj)}")

        try:
            appointment_date = convert_to_date(appointment.appointment_date)
            appointment_time = convert_to_time(appointment.appointment_time)
        except ValueError as e:
            logger.error(f"Date/Time conversion error: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))

        # Calculate fees
        payment = appointment.payment
        consultation_fee = float(payment.amount) * 0.8 if payment else 0
        service_charge = float(payment.amount) * 0.2 if payment else 0
        total_amount = float(payment.amount) if payment else 0

        # Prepare appointment data for PDF
        appointment_data = {
            "appointment_id": appointment.appointment_id,
            "appointment_number": appointment.appointment_number,
            "doctor_name": f"{appointment.doctor.title} {appointment.doctor.name}" if appointment.doctor else "N/A",
            "doctor_specialization": appointment.doctor.specialization if appointment.doctor else "N/A",
            "hospital_name": appointment.hospital.name if appointment.hospital else "N/A",
            "appointment_date": appointment_date,
            "appointment_time": appointment_time,
            "status": appointment.status,
            "consultation_fee": consultation_fee,
            "service_charge": service_charge,
            "total_amount": total_amount,
            "patient_name": f"{appointment.user.first_name} {appointment.user.last_name}" if appointment.user else "N/A",
            "patient_email": appointment.user.email if appointment.user else "N/A",
            "patient_phone": appointment.user.phone if appointment.user else "N/A"
        }

        # Generate PDF
        pdf_buffer = await PDFService.generate_appointment_receipt(appointment_data)

        # Prepare response
        filename = f"appointment_receipt_{appointment.appointment_number}.pdf"
        headers = {
            'Content-Disposition': f'attachment; filename="{filename}"',
            'Content-Type': 'application/pdf'
        }

        return Response(
            content=pdf_buffer.getvalue(),
            headers=headers,
            media_type='application/pdf'
        )

    except HTTPException:
        raise
    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Database error occurred while generating receipt"
        )
    except Exception as e:
        logger.error(f"Unexpected error generating receipt: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error generating receipt: {str(e)}"
        )

@router.delete("/{appointment_id}/cancel")
async def cancel_appointment(
    appointment_id: int,
    current_user: User = Depends(JWTBearer()),
    db: Session = Depends(get_db)
):
    """
    Cancel an appointment.
    Admin/Staff can cancel any appointment, regular users can only cancel their own.
    """
    try:
        appointment = (
            db.query(Appointment)
            .options(
                joinedload(Appointment.doctor),
                joinedload(Appointment.hospital),
                joinedload(Appointment.payment),
                joinedload(Appointment.user)
            )
            .filter(Appointment.appointment_id == appointment_id)
            .first()
        )

        if not appointment:
            raise HTTPException(status_code=404, detail="Appointment not found")

        # Authorization check
        if current_user.role not in ["Admin", "Staff"] and appointment.user_id != current_user.user_id:
            raise HTTPException(status_code=403, detail="Not authorized to cancel this appointment")

        # Validate cancellation
        if appointment.status == "Cancelled":
            raise HTTPException(status_code=400, detail="Appointment is already cancelled")
        
        if appointment.status == "Completed":
            raise HTTPException(status_code=400, detail="Cannot cancel completed appointments")

        appointment_datetime = datetime.combine(
            appointment.appointment_date,
            appointment.appointment_time
        )
        if appointment_datetime < datetime.now():
            raise HTTPException(status_code=400, detail="Cannot cancel past appointments")

        # Update appointment status
        appointment.status = "Cancelled"
        appointment.updated_at = datetime.now()

        # Update payment status if exists
        if appointment.payment:
            appointment.payment.payment_status = "Failed"
            appointment.payment.updated_at = datetime.now()

        # Get details for response
        doctor_name = f"{appointment.doctor.title} {appointment.doctor.name}" if appointment.doctor else None
        hospital_name = appointment.hospital.name if appointment.hospital else None

        db.commit()

        return {
            "message": "Appointment cancelled successfully",
            "appointment_id": appointment_id,
            "appointment_number": appointment.appointment_number,
            "appointment_details": {
                "doctor_name": doctor_name,
                "hospital_name": hospital_name,
                "appointment_date": appointment.appointment_date.strftime("%Y-%m-%d"),
                "appointment_time": appointment.appointment_time.strftime("%I:%M %p"),
                "status": "Cancelled",
                "payment_status": "Failed" if appointment.payment else None
            }
        }

    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error during cancellation: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Could not cancel appointment due to database error"
        )
    except Exception as e:
        logger.error(f"Unexpected error during cancellation: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
    
from pydantic import BaseModel

class UpdateAppointmentStatusRequest(BaseModel):
    status: str

@router.patch("/{appointment_id}/status")
async def update_appointment_status(
    appointment_id: int,
    status_data: UpdateAppointmentStatusRequest,  # Accept status as part of the request body
    current_user: User = Depends(JWTBearer()),
    db: Session = Depends(get_db)
):
    """
    Update appointment status.
    Only Admin and Staff can update appointment status.
    Valid statuses: Pending, Completed, Cancelled
    """
    try:
        # Check if user has permission
        if current_user.role not in ["Admin", "Staff"]:
            raise HTTPException(
                status_code=403,
                detail="Not authorized to update appointment status"
            )

        # Extract status from the request body
        status = status_data.status

        # Validate status
        valid_statuses = ["Pending", "Completed", "Cancelled"]  # Only 3 states
        if status not in valid_statuses:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
            )

        appointment = (
            db.query(Appointment)
            .options(
                joinedload(Appointment.doctor),
                joinedload(Appointment.hospital),
                joinedload(Appointment.user)
            )
            .filter(Appointment.appointment_id == appointment_id)
            .first()
        )

        if not appointment:
            raise HTTPException(status_code=404, detail="Appointment not found")

        # Update appointment status
        appointment.status = status
        appointment.updated_at = datetime.now()

        db.commit()

        return {
            "message": "Appointment status updated successfully",
            "appointment_id": appointment_id,
            "appointment_number": appointment.appointment_number,
            "new_status": status,
            "appointment_details": {
                "doctor_name": f"{appointment.doctor.title} {appointment.doctor.name}" if appointment.doctor else None,
                "hospital_name": appointment.hospital.name if appointment.hospital else None,
                "appointment_date": appointment.appointment_date.strftime("%Y-%m-%d"),
                "appointment_time": appointment.appointment_time.strftime("%I:%M %p"),
            }
        }

    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error during status update: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Could not update appointment status due to database error"
        )
    except Exception as e:
        logger.error(f"Unexpected error during status update: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )