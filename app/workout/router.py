from fastapi import APIRouter, HTTPException
from app.workout.schemas import WorkoutManualRequest, WorkoutRegenerateRequest, WorkoutRecommendationResponse
from app.workout.service import WorkoutService

router = APIRouter()
service = WorkoutService()

@router.post("/manual", response_model=WorkoutRecommendationResponse)
async def manual_recommend_workout(req: WorkoutManualRequest):
    try:
        return await service.generate(req.user_profile, req.history)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/batch")
async def batch_recommend_workout():
    return {"status": "batch triggered"}

@router.post("/{date}/regenerate", response_model=WorkoutRecommendationResponse)
async def regenerate_workout(date: str, req: WorkoutRegenerateRequest):
    return await service.regenerate(req.user_profile, req.history)

@router.get("/{id}/explanation")
async def workout_explanation(id: str):
    return await service.explain(id)
