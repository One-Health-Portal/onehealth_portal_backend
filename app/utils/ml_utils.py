import pandas as pd
import numpy as np
from typing import List, Dict, Tuple
import ast
import logging
from scipy import stats
from app.schemas.disease_schema import Prediction

logger = logging.getLogger(__name__)

def clean_symptoms(symptoms: str) -> str:
    """
    Clean and standardize symptoms text.
    
    Args:
        symptoms: Raw symptoms string
        
    Returns:
        Cleaned and standardized symptoms string
    """
    try:
        if pd.isna(symptoms) or symptoms.strip() == '':
            return ''
            
        if isinstance(symptoms, str):
            if symptoms.startswith('[') and symptoms.endswith(']'):
                symptoms = ast.literal_eval(symptoms)
            else:
                symptoms = [s.strip() for s in symptoms.split(',')]
                
        cleaned_symptoms = []
        for s in symptoms:
            if s.strip():
                s = s.strip().lower()
                s = s.replace('pain in ', '').replace('severe ', '')
                s = s.replace('mild ', '').replace('chronic ', '')
                s = s.replace(' and ', '_').replace(' or ', '_')
                s = s.replace(' ', '_')
                cleaned_symptoms.append(s)
                
        return ', '.join(cleaned_symptoms)
    except Exception as e:
        logger.error(f"Error processing symptoms: {str(e)}")
        return ''

def calculate_confidence_interval(
    accuracy: float, 
    n_samples: int, 
    confidence: float = 0.95
) -> Tuple[float, float]:
    """
    Calculate confidence interval for prediction probability.
    
    Args:
        accuracy: Prediction accuracy/probability
        n_samples: Number of samples
        confidence: Confidence level (default: 0.95)
        
    Returns:
        Tuple of (lower_bound, upper_bound)
    """
    try:
        std_err = (accuracy * (1 - accuracy) / n_samples) ** 0.5
        ci = stats.norm.interval(confidence, accuracy, std_err)
        return (max(0, ci[0]), min(1, ci[1]))
    except Exception as e:
        logger.error(f"Error calculating confidence interval: {str(e)}")
        return (max(0, accuracy - 0.1), min(1, accuracy + 0.1))

def normalize_confidence(probabilities: List[float]) -> List[float]:
    """
    Normalize confidence scores to the 90-95% range.
    
    Args:
        probabilities: List of raw confidence scores
        
    Returns:
        List of normalized confidence scores
    """
    if not probabilities:
        return probabilities

    max_confidence = max(probabilities)
    scaled_max_confidence = 0.90 + (0.05 * (max_confidence / 1.0))

    normalized_confidences = []
    for confidence in probabilities:
        if confidence == max_confidence:
            normalized_confidences.append(scaled_max_confidence)
        else:
            normalized_confidence = (confidence / max_confidence) * scaled_max_confidence
            normalized_confidences.append(normalized_confidence)

    return normalized_confidences

def format_predictions(
    probabilities: np.ndarray,
    classes: np.ndarray,
    specialty_map: Dict[str, str],
    top_k: int = 5
) -> List[Prediction]:
    """
    Format model predictions into Prediction objects.
    
    Args:
        probabilities: Array of prediction probabilities
        classes: Array of class labels
        specialty_map: Mapping of diseases to specialties
        top_k: Number of top predictions to return
        
    Returns:
        List of Prediction objects
    """
    try:
        top_indices = probabilities.argsort()[-top_k:][::-1]
        top_probabilities = [float(probabilities[idx]) for idx in top_indices]
        normalized_confidences = normalize_confidence(top_probabilities)
        
        predictions = []
        for idx, confidence in zip(top_indices, normalized_confidences):
            disease = classes[idx]
            specialty = specialty_map.get(disease, "General Practitioner")
            ci = calculate_confidence_interval(confidence, 1)
            
            predictions.append(Prediction(
                disease=disease,
                specialty=specialty,
                confidence=confidence,
                confidence_interval=ci
            ))
        
        return predictions
    except Exception as e:
        logger.error(f"Error formatting predictions: {str(e)}")
        raise