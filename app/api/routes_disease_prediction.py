from fastapi import APIRouter, HTTPException, Depends, status
from app.schemas.disease_schema import SymptomsInput, PredictionResponse
from app.utils.ml_utils import clean_symptoms, format_predictions
from app.core.jwt_auth import JWTBearer
from app.models.user import User
from sqlalchemy.orm import Session
from app.db.connection import get_db
import joblib
import os
import logging
from typing import Dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()
jwt_bearer = JWTBearer()

class ModelLoader:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModelLoader, cls).__new__(cls)
            cls._instance.initialized = False
        return cls._instance

    def __init__(self):
        if not self.initialized:
            self.model = None
            self.vectorizer = None
            self.label_encoder = None
            self.disease_specialty_map = None
            self.load_components()
            self.initialized = True

    def load_components(self) -> None:
        """Load ML model components."""
        try:
            base_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'app', 'mlmodels')
            model_path = os.path.join(base_dir, 'random_forest_model.joblib')
            vectorizer_path = os.path.join(base_dir, 'tfidf_vectorizer.joblib')
            encoder_path = os.path.join(base_dir, 'label_encoder.joblib')
            specialty_map_path = os.path.join(base_dir, 'disease_specialty_map.joblib')

            required_files = [model_path, vectorizer_path, encoder_path, specialty_map_path]
            missing_files = [p for p in required_files if not os.path.exists(p)]
            if missing_files:
                raise FileNotFoundError(f"Missing required files: {', '.join(missing_files)}")

            self.model = joblib.load(model_path)
            self.vectorizer = joblib.load(vectorizer_path)
            self.label_encoder = joblib.load(encoder_path)
            self.disease_specialty_map = joblib.load(specialty_map_path)
            logger.info("ML components loaded successfully.")
        except Exception as e:
            logger.error(f"Error loading ML components: {str(e)}")
            raise RuntimeError(f"Failed to load ML components: {str(e)}")

    def get_components_status(self) -> Dict[str, bool]:
        """Get the loading status of ML components."""
        return {
            "model_loaded": self.model is not None,
            "vectorizer_loaded": self.vectorizer is not None,
            "label_encoder_loaded": self.label_encoder is not None,
            "specialty_map_loaded": self.disease_specialty_map is not None
        }

    def predict(self, symptoms: str) -> PredictionResponse:
        """Predict diseases based on symptoms."""
        try:
            cleaned_symptoms = clean_symptoms(symptoms)
            if not cleaned_symptoms:
                raise ValueError("No valid symptoms after cleaning.")

            symptoms_vector = self.vectorizer.transform([cleaned_symptoms])
            probabilities = self.model.predict_proba(symptoms_vector)[0]
            predictions = format_predictions(
                probabilities=probabilities,
                classes=self.label_encoder.classes_,
                specialty_map=self.disease_specialty_map
            )
            return PredictionResponse(predictions=predictions, input_symptoms=symptoms)
        except Exception as e:
            logger.error(f"Prediction error: {str(e)}")
            raise RuntimeError(f"Error making prediction: {str(e)}")

model_loader = ModelLoader()

@router.post("/predict", response_model=PredictionResponse, status_code=status.HTTP_200_OK)
async def predict_diseases(
    symptoms_input: SymptomsInput,
    db: Session = Depends(get_db),
    current_user: User = Depends(jwt_bearer)
):
    """Predict diseases based on user-provided symptoms."""
    try:
        if not symptoms_input.symptoms.strip():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Symptoms cannot be empty.")

        logger.info(f"Prediction request from user {current_user.supabase_uid}.")
        prediction_response = model_loader.predict(symptoms_input.symptoms)
        logger.info(f"Prediction successful for user {current_user.supabase_uid}.")
        return prediction_response
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error in predict_diseases for user {current_user.supabase_uid}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/health")
async def health_check(
    db: Session = Depends(get_db),
    current_user: User = Depends(jwt_bearer)
):
    """Check the health status of ML components."""
    try:
        logger.info(f"Health check requested by user {current_user.supabase_uid}.")
        status_info = model_loader.get_components_status()
        status_info["status"] = "healthy" if all(status_info.values()) else "unhealthy"
        return status_info
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Health check failed: {str(e)}")