import os
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func
from typing import List, Tuple
from datetime import date, datetime, time, timedelta
from app.db.connection import get_db
from app.models.hospital_doctor import HospitalDoctor
from app.models.appointment import Appointment
from app.schemas.appointment_schema import (
    AvailableTimeSlotsResponse,
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
            "hospital_name": appointment.hospital.name if appointment.hospital else None
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

    booked_slots = {}
    for appointment in appointments:
        time_key = appointment.appointment_time.strftime("%H:%M:%S")
        booked_slots[time_key] = {
            "appointment_number": appointment.appointment_number,
            "status": appointment.status,
            "note": appointment.note
        }

    current_time = start_datetime
    while current_time < end_datetime:
        slot_time = current_time.time()
        slot_time_str = slot_time.strftime("%H:%M:%S")
        formatted_time = slot_time.strftime("%I:%M %p")
        
        if selected_date == current_datetime.date() and current_time <= current_datetime:
            unavailable_slots.append({
                "time": formatted_time,
                "available": False
            })
        elif slot_time_str in booked_slots:
            unavailable_slots.append({
                "time": formatted_time,
                "available": False
            })
        else:
            available_slots.append({
                "time": formatted_time,
                "available": True
            })

        current_time += timedelta(minutes=30)

    return available_slots, unavailable_slots

@router.get("/doctors/{doctor_id}/appointments", response_model=AvailableTimeSlotsResponse)
async def get_doctor_appointments(
    doctor_id: int,
    hospital_id: int,
    selected_date: date,
    db: Session = Depends(get_db)
):
    """
    Retrieve all appointments and calculate available time slots for a specific doctor 
    at a specific hospital for a selected date.
    """
    try:
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

        appointments = (
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
            .all()
        )

        available_slots, unavailable_slots = calculate_detailed_time_slots(
            availability.availability_start_time,
            availability.availability_end_time,
            appointments,
            selected_date
        )

        formatted_appointments = format_appointments(appointments)

        return {
            "available_slots": available_slots,
            "unavailable_slots": unavailable_slots,
            "appointments": formatted_appointments
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
    """
    try:
        last_appointment = db.query(Appointment).order_by(Appointment.appointment_id.desc()).first()
        if last_appointment:
            last_number = int(last_appointment.appointment_number.split("-")[-1])
            new_number = last_number + 1
        else:
            new_number = 1

        appointment_number = f"APPT-NO-{new_number}"

        current_timestamp = datetime.now()

        try:
            appointment_time = datetime.strptime(appointment_data.appointment_time, "%I:%M %p").time()
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid time format. Use 'HH:MM AM/PM'."
            )

        new_appointment = Appointment(
            user_id=current_user.user_id,
            doctor_id=appointment_data.doctor_id,
            hospital_id=appointment_data.hospital_id,
            appointment_date=appointment_data.appointment_date,
            appointment_time=appointment_time,
            status='Pending',
            appointment_number=appointment_number,
            note=appointment_data.note,
            created_at=current_timestamp,
            updated_at=current_timestamp
        )

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
        raise HTTPException(
            status_code=500, 
            detail="Could not book appointment"
        )
    except ValueError as e:
        logger.error(f"Value error: {str(e)}")
        raise HTTPException(
            status_code=400, 
            detail="Invalid time format"
        )

@router.get("/history", response_model=List[AppointmentResponse])
async def get_appointment_history(
    current_user: User = Depends(JWTBearer()),
    db: Session = Depends(get_db)
):
    """
    Retrieve the appointment history for the authenticated user.
    """
    try:
        appointments = (
            db.query(Appointment)
            .options(
                joinedload(Appointment.doctor),
                joinedload(Appointment.hospital),
                joinedload(Appointment.payment)
            )
            .filter(Appointment.user_id == current_user.user_id)
            .all()
        )

        if not appointments:
            logger.debug("No appointments found for user_id: %s", current_user.user_id)
            raise HTTPException(status_code=404, detail="No appointments found")

        formatted_appointments = []
        for appointment in appointments:
            appointment_date = (
                appointment.appointment_date.date()
                if isinstance(appointment.appointment_date, datetime)
                else appointment.appointment_date
            )

            if isinstance(appointment.appointment_time, str):
                appointment_time = datetime.strptime(appointment.appointment_time, "%I:%M %p").time()
            else:
                appointment_time = appointment.appointment_time

            appointment_dict = {
                "user_id": appointment.user_id,
                "doctor_id": appointment.doctor_id,
                "hospital_id": appointment.hospital_id,
                "appointment_date": appointment_date,
                "appointment_time": appointment_time,
                "status": appointment.status,
                "note": appointment.note,
                "appointment_number": appointment.appointment_number,
                "appointment_id": appointment.appointment_id,
                "created_at": appointment.created_at,
                "updated_at": appointment.updated_at,
                "payment_status": appointment.payment.payment_status if appointment.payment else "Pending",
                "total_amount": appointment.payment.amount if appointment.payment else 0.0,
            }

            if appointment.doctor:
                appointment_dict["doctor_name"] = appointment.doctor.name
                appointment_dict["doctor_specialization"] = appointment.doctor.specialization
            
            if appointment.hospital:
                appointment_dict["hospital_name"] = appointment.hospital.name

            formatted_appointments.append(AppointmentResponse(**appointment_dict))

        return formatted_appointments
    except SQLAlchemyError as e:
        logger.error("Database error: %s", str(e))
        raise HTTPException(status_code=500, detail="Could not retrieve appointments")
    
@router.get("/{appointment_id}/receipt")
async def get_appointment_receipt(
    appointment_id: int,
    current_user: User = Depends(JWTBearer()),
    db: Session = Depends(get_db)
):
    """
    Generate and return a PDF receipt for an appointment.
    """
    try:
        appointment = (
            db.query(Appointment)
            .options(
                joinedload(Appointment.doctor),
                joinedload(Appointment.hospital),
                joinedload(Appointment.payment)
            )
            .filter(Appointment.appointment_id == appointment_id)
            .first()
        )

        if not appointment:
            raise HTTPException(status_code=404, detail="Appointment not found")

        if current_user.role not in ["Admin", "Staff"] and appointment.user_id != current_user.user_id:
            raise HTTPException(status_code=403, detail="Not authorized to view this receipt")

        def convert_to_date(date_obj):
            if isinstance(date_obj, datetime):
                return date_obj.date()
            elif isinstance(date_obj, date):
                return date_obj
            elif isinstance(date_obj, str):
                date_formats = [
                    "%Y-%m-%d", 
                    "%Y-%m-%d %H:%M:%S", 
                    "%d-%m-%Y", 
                    "%m-%d-%Y"
                ]
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

        payment = appointment.payment

        appointment_data = {
            "appointment_id": appointment.appointment_id,
            "appointment_number": appointment.appointment_number,
            "doctor_name": f"{appointment.doctor.title} {appointment.doctor.name}",
            "doctor_specialization": appointment.doctor.specialization,
            "hospital_name": appointment.hospital.name,
            "appointment_date": appointment_date,
            "appointment_time": appointment_time,
            "status": appointment.status,
            "consultation_fee": float(payment.amount) * 0.8 if payment else 0,
            "service_charge": float(payment.amount) * 0.2 if payment else 0,
            "total_amount": float(payment.amount) if payment else 0
        }

        pdf_buffer = await PDFService.generate_appointment_receipt(appointment_data)

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
        import traceback
        logger.error(f"Unexpected error generating receipt: {traceback.format_exc()}")
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
    Cancel an appointment and update its payment status
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

        if current_user.role not in ["Admin", "Staff"] and appointment.user_id != current_user.user_id:
            raise HTTPException(status_code=403, detail="Not authorized to cancel this appointment")

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

        appointment.status = "Cancelled"
        appointment.updated_at = datetime.now()

        if appointment.payment:
            appointment.payment.payment_status = "Failed"
            appointment.payment.updated_at = datetime.now()

        doctor_name = f"{appointment.doctor.title} {appointment.doctor.name}" if appointment.doctor else None
        hospital_name = appointment.hospital.name if appointment.hospital else None

        db.commit()

        response_data = {
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

        return response_data

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
