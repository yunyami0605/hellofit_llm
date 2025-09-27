import os
from pprint import pprint
import uuid
import random
from typing import Dict, List
from datetime import date, timedelta

from fastapi import HTTPException
from langchain_core.output_parsers import JsonOutputParser
from langchain.output_parsers import OutputFixingParser
from langchain_openai import ChatOpenAI

from app.core.logger import logger
from app.core.vectorstore import FoodVectorStore
from app.diet.prompt import diet_auto_recommend_prompt, diet_regenerate_prompt, diet_regenerate_day_prompt
from app.diet.schemas import DietRecommendation, FoodRecord, MealRecord


class DietService:
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo-0125",
            temperature=0.7,
            max_tokens=1024
        )
        self.parser = OutputFixingParser.from_llm(
            llm=self.llm,
            parser=JsonOutputParser()
        )

        # 벡터스토어 로드
        self.food_store = FoodVectorStore()
        self.food_store.load_index()
        self.retriever = self.food_store.get_retriever(k=20)

    def _make_food_record(self, fd) -> FoodRecord:
        """DB weight 기준으로 영양소 값을 보정"""
        weight = fd.metadata.get("weight", 100) or 100
        factor = float(weight) / 100.0

        def to_int(value):
            return int(round(float(value) * factor))

        return FoodRecord(
            name=fd.metadata["rep_food_name"],
            calories=to_int(fd.metadata["kcal"]),
            protein=to_int(fd.metadata["protein"]),
            carbs=to_int(fd.metadata["carbs"]),
            fat=to_int(fd.metadata["fat"]),
        )

    def _match_foods_with_db(self, foods_from_llm, docs):
        """LLM이 준 음식 리스트를 DB 기반 FoodRecord로 변환"""
        results = []
        for f in foods_from_llm:
            name = f.get("name", "").lower().strip()
            matched_doc = next(
                (doc for doc in docs if doc.metadata["rep_food_name"].lower().strip() == name),
                None
            )
            if matched_doc:
                results.append(self._make_food_record(matched_doc))
            else:
                logger.warning(f"[DietService] 후보 외 음식 발견: {f.get('name')}")
        return results

    async def auto_generate(
        self, user_profile: dict, history: Dict[date, Dict[str, MealRecord]]
    ) -> List[DietRecommendation]:
        today = date.today()
        dates = {f"today+{i}": (today + timedelta(days=i)).isoformat() for i in range(3)}

        # 1. 최근 30일 이내 기록만 사용
        cutoff = today - timedelta(days=30)
        filtered_history = {
            d.isoformat(): {meal: m.dict() for meal, m in meals.items()}
            for d, meals in history.items()
            if d >= cutoff
        }

        # 2. 음식 후보 (retriever)
        docs = await self.retriever.ainvoke("식단 추천용 음식 후보")
        foods_context = "\n".join([doc.page_content for doc in docs])

        # 3. LLM 호출
        chain = diet_auto_recommend_prompt | self.llm | self.parser
        result = await chain.ainvoke({
            "user_profile": user_profile,
            "history": filtered_history,
            "today": today.isoformat(),
            "today+1": dates["today+1"],
            "today+2": dates["today+2"],
            "foods_context": foods_context,
        })

        # 4. 결과 → DB weight 기준으로 변환
        recommendations: List[DietRecommendation] = []
        for day_str, meals in (result or {}).items():
            if not isinstance(meals, dict):
                continue
            for meal_type, meal_data in meals.items():
                foods = self._match_foods_with_db(meal_data.get("foods", []), docs)

                # fallback
                if not foods:
                    fallback_docs = random.sample(docs, k=min(3, len(docs)))
                    foods = [self._make_food_record(fd) for fd in fallback_docs]
                    logger.warning(f"[DietService] {day_str} {meal_type} → fallback 음식 사용")

                rec = DietRecommendation(
                    recommendation_id=str(uuid.uuid4()),
                    date=date.fromisoformat(day_str),
                    meal_type=meal_type,
                    foods=foods,
                    explanation=meal_data.get("explanation", "")
                )
                recommendations.append(rec)

        # 5. 누락된 끼니 보정
        required_meals = ["BREAKFAST", "LUNCH", "DINNER"]
        for offset in range(3):
            day = today + timedelta(days=offset)
            existing_meals = {rec.meal_type for rec in recommendations if rec.date == day}
            missing_meals = set(required_meals) - existing_meals

            if missing_meals:
                logger.warning(f"[DietService] {day.isoformat()} 누락된 끼니 발견 → {missing_meals}")
                fallback_docs = random.sample(docs, k=min(3, len(docs)))
                fallback_foods = [self._make_food_record(fd) for fd in fallback_docs]
                for m in missing_meals:
                    recommendations.append(DietRecommendation(
                        recommendation_id=str(uuid.uuid4()),
                        date=day,
                        meal_type=m,
                        foods=fallback_foods,
                        explanation="자동 보정된 끼니"
                    ))

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

        serialized_history = {
            d.isoformat(): {meal: m.dict() for meal, m in meals.items()}
            for d, meals in history.items()
        }

        docs = await self.retriever.ainvoke("식단 추천용 음식 후보")
        foods_context = "\n".join([doc.page_content for doc in docs])

        chain = diet_regenerate_prompt | self.llm | self.parser
        result = await chain.ainvoke({
            "user_profile": user_profile,
            "history": serialized_history,
            "date": target.isoformat(),
            "meal_type": meal_type,
            "foods_context": foods_context,
        })

        # DB 기준 변환
        filtered_foods = self._match_foods_with_db(result.get("foods", []), docs)

        if not filtered_foods:  # fallback
            fallback_docs = random.sample(docs, k=min(3, len(docs)))
            filtered_foods = [self._make_food_record(fd) for fd in fallback_docs]
            logger.warning(f"[DietService] regenerate {meal_type} → fallback 음식 사용")

        regenerated = DietRecommendation(
            recommendation_id=str(uuid.uuid4()),
            date=target,
            meal_type=meal_type,
            foods=filtered_foods,
            explanation=result.get("explanation", "자동 생성된 식단")
        )

        return [regenerated]

    async def regenerate_day(
        self,
        target_date: str,
        user_profile: dict,
        history: Dict[date, Dict[str, MealRecord]]
    ) -> List[DietRecommendation]:
        pprint(target_date)
        try:
            target = date.fromisoformat(target_date)
        except ValueError:
            raise HTTPException(status_code=400, detail="잘못된 날짜 형식입니다. (YYYY-MM-DD)")

        serialized_history = {
            d.isoformat(): {meal: m.dict() for meal, m in meals.items()}
            for d, meals in history.items()
        }

        docs = await self.retriever.ainvoke("식단 추천용 음식 후보")
        foods_context = "\n".join([doc.page_content for doc in docs])

        chain = diet_regenerate_day_prompt | self.llm | self.parser
        result = await chain.ainvoke({
            "user_profile": user_profile,
            "history": serialized_history,
            "date": target.isoformat(),
            "foods_context": foods_context,
        })

        recommendations: List[DietRecommendation] = []
        day_result = result.get(target.isoformat(), {})

        for meal_type, meal_data in day_result.items():
            foods = self._match_foods_with_db(meal_data.get("foods", []), docs)

            if not foods:  # fallback
                fallback_docs = random.sample(docs, k=min(3, len(docs)))
                foods = [self._make_food_record(fd) for fd in fallback_docs]

            recommendations.append(DietRecommendation(
                recommendation_id=str(uuid.uuid4()),
                date=target,
                meal_type=meal_type,
                foods=foods,
                explanation=meal_data.get("explanation", "")
            ))

        pprint(recommendations)
        return recommendations
