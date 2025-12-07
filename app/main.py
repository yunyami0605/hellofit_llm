from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from app.core.exceptions import AppException, app_exception_handler
from app.chat.router import router as chat_router
try:
    from app.diet.router import router as diet_router
except Exception:
    diet_router = None
try:
    from app.workout.router import router as workout_router
except Exception:
    workout_router = None

app = FastAPI(title="HelloFit LLM API", version="0.1.0")

# 예외 핸들러 등록
app.add_exception_handler(AppException, app_exception_handler)

# 라우터 등록
if diet_router is not None:
    app.include_router(diet_router, prefix="/recommend/diet", tags=["Diet API (식단))"])
if workout_router is not None:
    app.include_router(workout_router, prefix="/recommend/workout", tags=["Workout API (운동)"])
app.include_router(chat_router, tags=["Chat API"])

@app.get("/health")
def health_check():
    return {"status": "ok"}

