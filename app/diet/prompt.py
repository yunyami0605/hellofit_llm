from langchain.prompts import ChatPromptTemplate

diet_auto_recommend_prompt = ChatPromptTemplate.from_template("""
당신은 개인 맞춤 식단 코치입니다.

[유저 프로필]
{user_profile}

[지난 식단 기록(최대 30일) + 미래 추천 기록(있으면 그대로 유지)]
{history}

---
요구사항:
1. 오늘 날짜({today})를 포함하여 **정확히 7일치** 식단을 추천하세요. (오늘 + 6일 뒤까지)
2. 각 날짜에는 반드시 BREAKFAST, LUNCH, DINNER 세 끼니가 포함되어야 합니다.
3. 이미 미래 추천 기록이 있는 경우 절대 수정하지 말고 그대로 유지하며, 없는 날짜와 끼니만 새로 채워주세요.
4. 각 끼니별로 3~5개 음식을 추천하세요.
5. 각 음식은 JSON 객체로, {{"name": str, "calories": int, "protein": int, "carbs": int, "fat": int}} 형식으로 작성하세요.
6. 유저의 금지 음식이 있다면 절대 포함하지 마세요.
7. 최종 출력은 다른 텍스트를 출력하지 말고, **반드시 JSON만** 출력하세요.

예시 출력:
{{
  "{today}": {{
    "BREAKFAST": {{
      "foods": [
        {{"name": "계란후라이", "calories": 150, "protein": 12, "carbs": 1, "fat": 10}},
        {{"name": "삶은 감자", "calories": 120, "protein": 3, "carbs": 26, "fat": 0}}
      ],
      "explanation": "단백질과 탄수화물 균형"
    }},
    "LUNCH": {{
      "foods": [...],
      "explanation": "..."
    }},
    "DINNER": {{
      "foods": [...],
      "explanation": "..."
    }}
  }},
  "{today+1}": {{ ... }},
  "{today+2}": {{ ... }},
  "{today+3}": {{ ... }},
  "{today+4}": {{ ... }},
  "{today+5}": {{ ... }},
  "{today+6}": {{ ... }}
}}
""")

diet_regenerate_prompt = ChatPromptTemplate.from_template("""
당신은 개인 맞춤 식단 코치입니다.

[유저 프로필]
{user_profile}

[전체 기록]
- 지난 30일 실제 기록
- 이미 추천된 미래 7일치 기록
{history}

[재생성 요청]
- 날짜: {date}
- 끼니: {meal_type}

---
요구사항:
1. 위 날짜의 {meal_type} 식단만 새로 추천하세요.
2. 다른 날짜나 다른 끼니 기록은 절대 수정하지 마세요.
3. 식단은 3~5개의 음식으로 구성하세요.
4. 각 음식에는 반드시 칼로리(calories), 단백질(protein), 탄수화물(carbs), 지방(fat)을 포함하세요.
5. 유저의 금지 음식이 있다면 절대 포함하지 마세요.
6. 결과는 반드시 JSON 형식으로만 출력하세요.

예시 출력:
{{
  "foods": [
    {{"name": "연어구이", "calories": 280, "protein": 25, "carbs": 0, "fat": 18}},
    {{"name": "현미밥", "calories": 200, "protein": 4, "carbs": 44, "fat": 1}},
    {{"name": "샐러드", "calories": 120, "protein": 3, "carbs": 10, "fat": 7}}
  ],
  "explanation": "단백질과 오메가3를 보충하는 저녁 식단"
}}
""")