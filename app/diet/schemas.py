from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import date
import uuid

class FoodRecord(BaseModel):
    name: str
    calories: float
    protein: float
    carbs: float
    fat: float

class MealRecord(BaseModel):
    foods: List[FoodRecord]
    explanation: str

# === Request ===
# 유저 식단 신규 생성 요청 API (회원가입 시,)
class DietNewRequest(BaseModel):
    meal_type: str = Field(..., example="DINNER")
    user_profile: Dict = Field(..., example={"age_group": "20s", "gender": "male", "height": 175, "weight": 70})
    history: Dict[date, str] = Field(
        ..., 
        example={
            "2025-09-23": "닭가슴살, 고구마",
            "2025-09-22": "현미밥, 두부",
            "2025-09-21": "샐러드, 연어"
        }
    )






# 추천 자동생성 요청
class DietAutoRequest(BaseModel):
    user_profile: Dict = Field(
        ..., 
        example={
            "age_group": "20s", 
            "gender": "male", 
            "height": 175, 
            "weight": 70,
            "forbidden_foods": ["햄버거", "콜라"]  # 금지 음식 예시
        }
    )
    # 오늘 포함 30일 전 기록 + 미래 추천 기록(최대 6일)까지 가능
    history: Dict[date, Dict[str, MealRecord]] = Field(
        ..., 
        example={
            "2025-08-25": {
                "BREAKFAST": {
                    "foods": [
                        {"name": "현미밥", "calories": 300, "protein": 6, "carbs": 65, "fat": 2},
                        {"name": "두부", "calories": 100, "protein": 10, "carbs": 3, "fat": 5}
                    ],
                    "explanation": "탄수화물과 단백질 균형"
                },
                "LUNCH": {
                    "foods": [
                        {"name": "닭가슴살", "calories": 200, "protein": 40, "carbs": 0, "fat": 5}
                    ],
                    "explanation": "고단백 점심"
                },
                "DINNER": {
                    "foods": [
                        {"name": "샐러드", "calories": 150, "protein": 5, "carbs": 10, "fat": 8}
                    ],
                    "explanation": "저칼로리 저녁"
                }
            },
            "2025-09-23": {
                "DINNER": {
                    "foods": [
                        {"name": "연어", "calories": 250, "protein": 22, "carbs": 0, "fat": 15}
                    ],
                    "explanation": "오메가3 섭취"
                }
            }
        }
    )

# 특정 날짜에서 특정 끼니 식단 재생성 요청
class DietRegenerateRequest(DietAutoRequest):
    meal_type: str = Field(..., example="DINNER")

class DietRecommendation(BaseModel):
    recommendation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    date: date
    meal_type: str   # "BREAKFAST" | "LUNCH" | "DINNER"
    foods: List[FoodRecord]
    explanation: str

# === Response ===
# 식단 추천 응답
class DietRecommendationResponse(BaseModel):
    recommendation_id: uuid.UUID = Field(..., example="550e8400-e29b-41d4-a716-446655440111")
    meal_type: str = Field(..., example="DINNER")
    foods: List[str] = Field(..., example=["닭가슴살 샐러드", "고구마", "블루베리"])
    explanation: Optional[str] = Field(None, example="단백질 위주의 저녁 식단입니다.")

