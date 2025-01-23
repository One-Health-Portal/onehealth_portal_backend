from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.connection import engine, Base
from datetime import datetime

# Import all routers
from app.api.routes_users import router as users_router
from app.api.routes_hospitals import router as hospitals_router
from app.api.routes_appointments import router as appointments_router
from app.api.routes_feedback import router as feedback_router
from app.api.routes_lab_tests import router as lab_tests_router
from app.api.routes_payments import router as payments_router
from app.api.routes_hospital_doctor import router as hospital_doctor_router
from app.api.routes_doctors import router as doctors_router
from app.api.routes_upload import router as upload_router
from app.api.routes_disease_prediction import router as disease_prediction_router
from app.api.routes_auth import router as auth_router
from app.api.routes_dashboard import router as dashboard_router
from app.api.routes_patients import router as patients_router
from app.api.routes_dashboard_appointments import router as dashboard_appointments_router
from app.api.routes_dashboard_doctor import router as dashboard_doctor_router
from app.api.routes_dashboard_user import router as dashboard_user_router  # Import the new router

# Import all models
from app.models.user import User
from app.models.hospital import Hospital
from app.models.appointment import Appointment
from app.models.feedback import Feedback
from app.models.doctor import Doctor
from app.models.payment import Payment
from app.models.lab_test import LabTest
from app.models.hospital_doctor import HospitalDoctor

import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Check for ML models directory
ML_MODELS_DIR = os.path.join(os.path.dirname(__file__), 'mlmodels')
if not os.path.exists(ML_MODELS_DIR):
    os.makedirs(ML_MODELS_DIR)
    logger.info(f"Created ML models directory at {ML_MODELS_DIR}")

# Initialize FastAPI app
app = FastAPI(
    title="One Health Portal API",
    description="API for managing healthcare services, appointments, and patient data",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database tables
try:
    Base.metadata.create_all(bind=engine)
    logger.info("Successfully initialized database tables")
except Exception as e:
    logger.error(f"Failed to initialize database tables: {str(e)}")
    raise

# Include all API routers
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])  # Add authentication router first
app.include_router(dashboard_router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(users_router, prefix="/api/users", tags=["Users"])
app.include_router(hospitals_router, prefix="/api/hospitals", tags=["Hospitals"])
app.include_router(appointments_router, prefix="/api/appointments", tags=["Appointments"])
app.include_router(feedback_router, prefix="/api/feedback", tags=["Feedback"])
app.include_router(lab_tests_router, prefix="/api/lab-tests", tags=["Lab Tests"])
app.include_router(payments_router, prefix="/api/payments", tags=["Payments"])
app.include_router(hospital_doctor_router, prefix="/api/hospital-doctor", tags=["Hospital-Doctor"])
app.include_router(doctors_router, prefix="/api/doctors", tags=["Doctors"])
app.include_router(upload_router, prefix="/api/upload", tags=["Upload"])
app.include_router(
    disease_prediction_router, 
    prefix="/api/disease-prediction", 
    tags=["Disease Prediction"]
)
app.include_router(patients_router, prefix="/api/patients", tags=["Patients"])
app.include_router(dashboard_appointments_router, prefix="/api/dashboard/appointments", tags=["Dashboard Appointments"])
app.include_router(dashboard_doctor_router, prefix="/api/dashboard/doctors", tags=["Dashboard Doctors"])
app.include_router(dashboard_user_router, prefix="/api/dashboard", tags=["Dashboard Users"])  # Add the new router

@app.get("/")
async def root():
    """
    Root endpoint that returns basic API information
    """
    return {
        "message": "Welcome to the One Health Portal API",
        "version": "1.0.0",
        "status": "operational",
        "documentation": "/docs",
        "redoc": "/redoc"
    }

@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring
    """
    try:
        # Check database connection
        db_status = "connected" if engine.connect() else "disconnected"
        
        # Check ML models
        required_ml_models = [
            'random_forest_model.joblib',
            'tfidf_vectorizer.joblib',
            'disease_specialty_map.joblib',
            'label_encoder.joblib'
        ]
        
        ml_models_status = all(
            os.path.exists(os.path.join(ML_MODELS_DIR, f))
            for f in required_ml_models
        )

        # Log missing files for debugging
        missing_files = [
            f for f in required_ml_models 
            if not os.path.exists(os.path.join(ML_MODELS_DIR, f))
        ]
        
        if missing_files:
            logger.warning(f"Missing ML model files: {missing_files}")

        return {
            "status": "healthy",
            "database": db_status,
            "ml_models": "loaded" if ml_models_status else "missing",
            "missing_files": missing_files if missing_files else None,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }