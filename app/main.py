import os
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from app.core.exceptions import AppException, app_exception_handler
from app.diet.router import router as diet_router
from app.workout.router import router as workout_router

app = FastAPI(title="HelloFit LLM API", version="0.1.0")

# 예외 핸들러 등록
app.add_exception_handler(AppException, app_exception_handler)

# 라우터 등록
app.include_router(diet_router, prefix="/recommend/diet", tags=["Diet API (식단))"])
app.include_router(workout_router, prefix="/recommend/workout", tags=["Workout API (운동)"])

@app.get("/health")
def health_check():
    return {"status": "ok"}

import requests

API_KEY = os.getenv("FOOD_API_KEY")
BASE_URL = "https://api.nal.usda.gov/fdc/v1"

def parse_food(food_json: dict):
    nutrients_map = {
        "Energy": "calories",
        "Protein": "protein",
        "Carbohydrate, by difference": "carbs",
        "Total lipid (fat)": "fat"
    }
    
    parsed = {
        "name": food_json.get("description", "Unknown"),
        "calories": 0,
        "protein": 0,
        "carbs": 0,
        "fat": 0
    }

    for nutrient in food_json.get("foodNutrients", []):
        name = nutrient.get("nutrientName")
        value = nutrient.get("value")
        if name in nutrients_map:
            parsed[nutrients_map[name]] = value
    
    return parsed

def get_food(fdc_id: int):
    url = f"{BASE_URL}/food/{fdc_id}"
    params = {"api_key": API_KEY}
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()

food_raw = get_food(1102650)
parsed = parse_food(food_raw)

print(parsed)