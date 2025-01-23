from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from typing import List
from app.db.connection import get_db
from app.models.appointment import Appointment
from app.models.doctor import Doctor
from app.models.user import User
from app.models.hospital import Hospital
from app.core.jwt_auth import JWTBearer
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/dashboard")
async def get_dashboard_data(
    current_user: User = Depends(JWTBearer()),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive dashboard data including:
    - Total appointments, doctors, and patients
    - Recent patients with their details (based on account creation timestamp)
    - Department distribution
    - Appointment analytics
    """
    try:
        # Get total counts
        total_appointments = db.query(Appointment).count()
        active_doctors = db.query(Doctor).filter(Doctor.is_active == True).count()
        total_patients = db.query(User).filter(User.role == "Patient").count()

        # Get recent patients based on account creation timestamp
        recent_patients_query = (
            db.query(User)
            .filter(User.role == "Patient")
            .order_by(User.created_at.desc())  # This will now sort by full timestamp
            .limit(5)
            .all()
        )

        recent_patients = []
        for patient in recent_patients_query:
            # Format the timestamp to include both date and time
            created_at_formatted = patient.created_at.strftime("%Y-%m-%d %H:%M:%S")
            
            recent_patients.append({
                "id": patient.user_id,
                "name": f"{patient.first_name} {patient.last_name}",
                "avatar": patient.profile_picture_url if patient.profile_picture_url else f"/api/placeholder/40/40?text={patient.first_name[0]}{patient.last_name[0]}",
                "created_at": created_at_formatted,
                # Add time components separately for more flexible frontend display
                "created_time": patient.created_at.strftime("%H:%M:%S"),
                "created_date": patient.created_at.strftime("%Y-%m-%d")
            })

        # Get department distribution
        department_stats = (
            db.query(
                Doctor.specialization,
                func.count(User.user_id).label('patients')
            )
            .join(Appointment, Doctor.doctor_id == Appointment.doctor_id)
            .join(User, Appointment.user_id == User.user_id)
            .group_by(Doctor.specialization)
            .all()
        )

        # Define colors for departments
        department_colors = {
            "Cardiology": "#FF6384",
            "Pediatrics": "#36A2EB",
            "Neurology": "#FFCE56",
            "Orthopedics": "#4BC0C0",
            "General Medicine": "#9966FF",
            "Dermatology": "#FF9F40",
        }

        department_distribution = [
            {
                "name": dept,
                "patients": count,
                "color": department_colors.get(dept, "#808080")
            }
            for dept, count in department_stats
        ]

        # Get appointment analytics for the last 7 days
        today = datetime.now().date()
        last_week = today - timedelta(days=6)
        
        appointment_stats = []
        for i in range(7):
            current_date = last_week + timedelta(days=i)
            try:
                day_stats = {
                    "day": current_date.strftime("%A"),
                    "appointments": db.query(Appointment).filter(
                        func.date(Appointment.appointment_date) == current_date
                    ).count(),
                    "visits": db.query(Appointment).filter(
                        func.date(Appointment.appointment_date) == current_date,
                        Appointment.status == "Completed"
                    ).count(),
                    "emergency": db.query(Appointment).filter(
                        func.date(Appointment.appointment_date) == current_date,
                        Appointment.note.ilike("%emergency%")
                    ).count()
                }
                appointment_stats.append(day_stats)
            except Exception as e:
                logger.error(f"Error fetching appointment stats for {current_date}: {str(e)}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Error fetching appointment stats for {current_date}"
                )

        return {
            "totalAppointments": total_appointments,
            "activeDoctors": active_doctors,
            "totalPatients": total_patients,
            "recentPatients": recent_patients,
            "departmentDistribution": department_distribution,
            "appointmentAnalytics": appointment_stats
        }

    except HTTPException as http_error:
        raise http_error
    except Exception as e:
        logger.error(f"Unexpected error fetching dashboard data: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while fetching dashboard data"
        )
    
@router.get("/admin-dashboard")
async def get_admin_dashboard_data(
    current_user: User = Depends(JWTBearer()),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive data for the Admin Dashboard, including:
    - Total users (Patients, Staff, Admins)
    - Active alerts (dummy data)
    - Daily log entries (dummy data)
    - User growth over time
    - User distribution by type
    - Recent activities (dummy data)
    """
    try:
        # 1. Total Users
        total_users = db.query(User).count()
        total_patients = db.query(User).filter(User.role == "Patient").count()
        total_staff = db.query(User).filter(User.role == "Staff").count()
        total_admins = db.query(User).filter(User.role == "Admin").count()

        # 2. Active Alerts (dummy data)
        active_alerts = 24  # Dummy value for active alerts

        # 3. Daily Log Entries (dummy data)
        daily_log_entries = 1200  # Dummy value for daily log entries

        # 4. User Growth (last 7 days)
        user_growth = []
        today = datetime.now().date()
        for i in range(7):
            date = today - timedelta(days=i)
            users_count = db.query(User).filter(func.date(User.created_at) == date).count()
            staff_count = db.query(User).filter(User.role == "Staff", func.date(User.created_at) == date).count()
            user_growth.append({
                "day": date.strftime("%a"),
                "users": users_count,
                "staff": staff_count,
            })

        # 5. User Distribution
        user_distribution = [
            {"name": "Patients", "value": total_patients, "color": "#2196F3"},
            {"name": "Staff", "value": total_staff, "color": "#4CAF50"},
            {"name": "Admins", "value": total_admins, "color": "#FFC107"},
        ]

        # 6. Recent Activities (dummy data)
        recent_activities = [
            {
                "id": 1,
                "activity": "New staff account created",
                "timestamp": "2024-01-08 14:30",
                "type": "User Management",
            },
            {
                "id": 2,
                "activity": "Security policy updated",
                "timestamp": "2024-01-08 13:15",
                "type": "Security",
            },
            {
                "id": 3,
                "activity": "Role permissions modified",
                "timestamp": "2024-01-08 12:00",
                "type": "Access Control",
            },
            {
                "id": 4,
                "activity": "System backup completed",
                "timestamp": "2024-01-08 11:30",
                "type": "System",
            },
            {
                "id": 5,
                "activity": "User role updated",
                "timestamp": "2024-01-08 10:45",
                "type": "User Management",
            },
        ]

        return {
            "total_users": total_users,
            "total_patients": total_patients,
            "total_staff": total_staff,
            "total_admins": total_admins,
            "active_alerts": active_alerts,
            "daily_log_entries": daily_log_entries,
            "user_growth": user_growth,
            "user_distribution": user_distribution,
            "recent_activities": recent_activities,
        }

    except Exception as e:
        logger.error(f"Unexpected error fetching admin dashboard data: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while fetching admin dashboard data"
        )