from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import date
import uuid

class WorkoutManualRequest(BaseModel):
    user_id: uuid.UUID
    log_date: date
    user_profile: Dict
    history: List[str]

class WorkoutRegenerateRequest(BaseModel):
    user_id: uuid.UUID
    log_date: date
    user_profile: Dict
    history: List[str]

class WorkoutRecommendationResponse(BaseModel):
    recommendation_id: uuid.UUID
    exercises: List[Dict] = Field(..., example=[{"name": "푸시업", "sets": 3, "reps": 15}])
    explanation: Optional[str]
