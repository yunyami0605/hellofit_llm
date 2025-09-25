import uuid
from app.workout.prompt import workout_recommend_prompt
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import JsonOutputParser
from app.core.logger import logger

class WorkoutService:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
        self.parser = JsonOutputParser()

    async def generate(self, user_profile: dict, history: list[str]):
        logger.info("[Workout] Generating recommendation")
        chain = workout_recommend_prompt | self.llm | self.parser
        result = await chain.ainvoke({"user_profile": user_profile, "history": history})

        return {
            "recommendation_id": str(uuid.uuid4()),
            "exercises": result.get("exercises", []),
            "explanation": result.get("explanation", "")
        }

    async def regenerate(self, user_profile: dict, history: list[str]):
        logger.info("[Workout] Regenerating recommendation")
        return await self.generate(user_profile, history)

    async def explain(self, recommendation_id: str):
        logger.info(f"[Workout] Explaining recommendation {recommendation_id}")
        return {"recommendation_id": recommendation_id, "explanation": "추천 이유 예시"}
