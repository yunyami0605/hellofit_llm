import os
from pprint import pprint
from typing import Dict, List
import uuid

from fastapi import HTTPException
from langchain_anthropic import ChatAnthropic
from langchain_mistralai import ChatMistralAI
from app.diet.prompt import diet_auto_recommend_prompt, diet_regenerate_prompt
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import JsonOutputParser
from app.core.logger import logger
from datetime import date, timedelta

from app.diet.schemas import DietRecommendation, FoodRecord, MealRecord
from langchain.output_parsers import OutputFixingParser
class DietService:
    def __init__(self):
        # self.llm = ChatOpenAI(model="gpt-4o-mini-instant", temperature=0.7)
        # self.llm = ChatOpenAI(model="gpt-3.5-turbo-0125", temperature=0.7)

        self.llm = ChatMistralAI(
            model="mistral-tiny",   # 최신 스몰 모델모델
            # model="mistral-small-2409",   # 최신 스몰 모델모델
            temperature=0.7,
            api_key=os.getenv("MISTRAL_API_KEY"),
        )

        # self.llm = ChatAnthropic(
        #     model="claude-3-haiku-20240307",
        #     temperature=0.7,
        #     max_tokens=1024
        # )

        # self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
        
        # self.parser = JsonOutputParser()
        self.parser = OutputFixingParser.from_llm(
            llm=self.llm,
            parser=JsonOutputParser()
        )

    async def auto_generate(self, user_profile: dict, history: Dict[date, Dict[str, MealRecord]]) -> List[DietRecommendation]:
        today = date.today()
        dates = {f"today+{i}": (today + timedelta(days=i)).isoformat() for i in range(7)}

        # 1. 오늘 기준 30일 이전 데이터는 버림
        cutoff = today - timedelta(days=30)
        filtered_history = {
            d.isoformat(): {meal: m.dict() for meal, m in meals.items()}
            for d, meals in history.items()
            if d >= cutoff
        }

        # 2. 프롬프트 준비
        chain = diet_auto_recommend_prompt | self.llm | self.parser
        result = await chain.ainvoke({
            "user_profile": user_profile,
            "history": filtered_history,
            "today": today.isoformat(),
            "today+1": dates["today+1"],
            "today+2": dates["today+2"],
            "today+3": dates["today+3"],
            "today+4": dates["today+4"],
            "today+5": dates["today+5"],
            "today+6": dates["today+6"]
        })

        # 3. 응답 파싱 (LLM이 반환하는 JSON = 날짜별 → 끼니별 → foods + explanation)
        recommendations: List[DietRecommendation] = []

        for day_str, meals in (result or {}).items():
            if not isinstance(meals, dict):
                continue
            for meal_type, meal_data in meals.items():
                if not isinstance(meal_data, dict):
                    continue

                foods = [
                    FoodRecord(
                        name=f["name"],
                        calories=f["calories"],
                        protein=f["protein"],
                        carbs=f["carbs"],
                        fat=f["fat"]
                    )
                    for f in meal_data.get("foods", [])
                ]

                rec = DietRecommendation(
                    recommendation_id=str(uuid.uuid4()),
                    date=date.fromisoformat(day_str),
                    meal_type=meal_type,
                    foods=foods,
                    explanation=meal_data.get("explanation", "")
                )
                recommendations.append(rec)

        if not recommendations:
            raise HTTPException(status_code=500, detail="식단 추천을 생성하지 못했습니다.")

        logger.info(f"[Diet] Auto-generated {len(recommendations)} recommendations")
        return recommendations


    async def regenerate(
        self, 
        target_date: str, 
        user_profile: dict, 
        history: Dict[date, Dict[str, MealRecord]], 
        meal_type: str
    ) -> List[DietRecommendation]:
        try:
            target = date.fromisoformat(target_date)
        except ValueError:
            raise HTTPException(status_code=400, detail="잘못된 날짜 형식입니다. (YYYY-MM-DD)")

        # history 직렬화
        serialized_history = {
            d.isoformat(): {meal: m.dict() for meal, m in meals.items()}
            for d, meals in history.items()
        }

        # 프롬프트 호출 (특정 날짜/끼니만 새로 생성)
        chain = diet_regenerate_prompt | self.llm | self.parser

        pprint(user_profile)
        pprint(serialized_history)
        pprint(target.isoformat())
        pprint(meal_type)
        pprint(history.items())
        result = await chain.ainvoke({
            "user_profile": user_profile,
            "history": serialized_history,
            "date": target.isoformat(),
            "meal_type": meal_type
        })
        pprint(result)

        # 새로 생성된 끼니
        regenerated = DietRecommendation(
            recommendation_id=str(uuid.uuid4()),
            date=target,
            meal_type=meal_type,
            foods=[
                FoodRecord(**f) for f in result.get("foods", []) if isinstance(f, dict)
            ],
            explanation=result.get("explanation", "")
        )
        pprint(regenerated)

        recommendations: List[DietRecommendation] = []
        for d, meals in history.items():
            for m_type, meal_data in meals.items():
                if d == target and m_type == meal_type:
                    # 해당 끼니는 regenerate 결과로 교체
                    recommendations.append(regenerated)
                else:
                    foods = [f for f in meal_data.foods]  # MealRecord.foods는 이미 FoodRecord 리스트
                    rec = DietRecommendation(
                        recommendation_id=str(uuid.uuid4()),
                        date=d,
                        meal_type=m_type,
                        foods=foods,
                        explanation=meal_data.explanation
                    )
                    recommendations.append(rec)

        return recommendations