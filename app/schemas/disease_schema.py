from pydantic import BaseModel, Field, validator
from typing import List, Tuple
from datetime import datetime

class SymptomsInput(BaseModel):
    """Schema for input symptoms request."""
    symptoms: str = Field(
        ..., 
        description="Comma-separated list of symptoms",
        example="fever, cough, headache",
        min_length=1,
        max_length=1000
    )

    @validator('symptoms')
    def validate_symptoms(cls, v):
        """Validate symptoms input."""
        if not v.strip():
            raise ValueError("Symptoms cannot be empty")
        if len(v.split(',')) > 20:  # Reasonable limit for number of symptoms
            raise ValueError("Too many symptoms provided. Maximum 20 symptoms allowed.")
        return v.strip()

class Prediction(BaseModel):
    """Schema for individual disease prediction."""
    disease: str = Field(
        ..., 
        description="Predicted disease name"
    )
    specialty: str = Field(
        ..., 
        description="Medical specialty"
    )
    confidence: float = Field(
        ..., 
        description="Confidence score (0-1)",
        ge=0.0, 
        le=1.0
    )
    confidence_interval: Tuple[float, float] = Field(
        ..., 
        description="Confidence interval (lower, upper)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "disease": "Common Cold",
                "specialty": "General Practitioner",
                "confidence": 0.92,
                "confidence_interval": [0.88, 0.96]
            }
        }

class PredictionResponse(BaseModel):
    """Schema for prediction response."""
    predictions: List[Prediction] = Field(
        ...,
        description="List of disease predictions",
        max_items=5
    )
    input_symptoms: str = Field(
        ...,
        description="Original input symptoms"
    )
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="Prediction timestamp"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "predictions": [
                    {
                        "disease": "Common Cold",
                        "specialty": "General Practitioner",
                        "confidence": 0.92,
                        "confidence_interval": [0.88, 0.96]
                    }
                ],
                "input_symptoms": "fever, cough, headache",
                "timestamp": "2024-01-19T10:30:00"
            }
        }