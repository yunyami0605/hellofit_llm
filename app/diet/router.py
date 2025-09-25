from fastapi import APIRouter, HTTPException
from app.diet.schemas import DietAutoRequest, DietNewRequest, DietRecommendation, DietRegenerateRequest, DietRecommendationResponse
from app.diet.service import DietService

router = APIRouter()
service = DietService()

# 유저에게 7일치 자동 식단 추천 생성 API
@router.post("/batch", summary="식단 추천 자동 생성 API", description="식단 추천 자동 생성 API", response_model=list[DietRecommendation])
async def batch_recommend_diet(req: DietAutoRequest):
    try:
        recommendations = await service.auto_generate(
            user_profile=req.user_profile,
            history=req.history
        )
        return recommendations
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 특정 날짜에서 특정 끼니 식단 재생성 요청 API
@router.post("/{date}/regenerate", summary="특정 날짜에서 특정 끼니 식단 재생성 요청 API", description="특정 날짜에서 특정 끼니 식단 재생성 요청 API", response_model=list[DietRecommendation])
async def regenerate_diet(date: str, req: DietRegenerateRequest):
    return await service.regenerate(date, req.user_profile, req.history, req.meal_type)

