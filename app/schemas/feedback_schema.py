# feedback_schema.py
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class FeedbackBase(BaseModel):
    user_id: int
    rating: int = Field(..., ge=1, le=5)
    comments: Optional[str] = None
    appointment_id: Optional[int] = None

class FeedbackCreate(FeedbackBase):
    pass

class FeedbackUpdate(BaseModel):
    rating: Optional[int] = Field(None, ge=1, le=5)
    comments: Optional[str] = None

class FeedbackResponse(FeedbackBase):
    feedback_id: int
    created_at: datetime

    class Config:
        from_attributes = True