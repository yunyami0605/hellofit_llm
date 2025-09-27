from langchain.prompts import ChatPromptTemplate

diet_auto_recommend_prompt = ChatPromptTemplate.from_template("""
당신은 개인 맞춤 식단 코치입니다.

[유저 프로필]
{user_profile}

[지난 식단 기록(최대 30일) + 미래 추천 기록(있으면 그대로 유지)]
{history}

[사용 가능한 음식 후보 (DB 기반 Top-K 검색 결과, 최대 20개)]
{foods_context}

---
요구사항:
1. 오늘 날짜({today})를 포함하여 **정확히 3일치** 식단을 추천하세요. (오늘 + 2일 뒤까지)
2. 각 날짜에는 반드시 BREAKFAST, LUNCH, DINNER 세 끼니가 포함되어야 합니다.
3. 이미 미래 추천 기록이 있는 경우 절대 수정하지 말고 그대로 유지하며, 없는 날짜와 끼니만 새로 채워주세요.
4. 각 끼니별로 3~5개 음식을 추천하세요.
5. 음식은 반드시 위 "음식 후보 리스트"에서만 선택하세요. (후보에 없는 음식은 생성하지 마세요)
6. 각 음식은 JSON 객체로, {{"name": str, "calories": int, "protein": int, "carbs": int, "fat": int}} 형식으로 작성하세요.
7. 유저의 금지 음식이 있다면 절대 포함하지 마세요.
8. 모든 숫자 필드는 반드시 정수 또는 소수(float) 값으로 채워야 하며, null 이나 빈 값은 허용되지 않습니다.
9. 최종 출력은 다른 텍스트를 출력하지 말고, **반드시 JSON만** 출력하세요.
⚠️ JSON 외의 설명, 문장, 주석을 절대 출력하지 마세요.
❗ 중요한 규칙:
- 반드시 3일치(오늘 포함 +2일) 식단이 있어야 합니다.
- 각 날짜에는 반드시 BREAKFAST, LUNCH, DINNER 세 끼니가 모두 포함되어야 합니다.
- 세 끼니 중 하나라도 빠지면 출력은 무효입니다. 
- 누락된 경우 절대 허용되지 않습니다.
                                                              
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
  "{today+2}": {{ ... }}
}}
""")


'''
diet_auto_recommend_prompt = ChatPromptTemplate.from_template("""
당신은 개인 맞춤 식단 코치입니다.

[유저 프로필]
{user_profile}

[지난 식단 기록(최대 30일) + 미래 추천 기록(있으면 그대로 유지)]
{history}

---
요구사항:
1. 오늘 날짜({today})를 포함하여 **정확히 3일치** 식단을 추천하세요. (오늘 + 2일 뒤까지)
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
  "{today+2}": {{ ... }}
}}
""")
'''

diet_regenerate_prompt = ChatPromptTemplate.from_template("""
당신은 개인 맞춤 식단 코치입니다.

[유저 프로필]
{user_profile}

[지난 식단 기록(최대 30일)]
{history}

[사용 가능한 음식 후보 (DB 기반 Top-K 검색 결과, 최대 20개)]
{foods_context}

---
요구사항:
1. 무조건 {date} 날짜의 {meal_type} 끼니 식단만 새로 생성하세요.
2. 반드시 BREAKFAST, LUNCH, DINNER 중 요청된 끼니({meal_type})만 출력하세요.
3. 음식은 반드시 위 "음식 후보 리스트"에서만 선택하세요. (후보에 없는 음식은 생성하지 마세요)
4. 3~5개의 음식을 추천하세요.
5. 음식은 {{"name": str, "calories": int, "protein": int, "carbs": int, "fat": int}} 형식의 JSON 객체여야 합니다.
6. 유저의 금지 음식이 있다면 절대 포함하지 마세요.
7. 모든 숫자 필드는 반드시 정수 또는 소수(float) 값으로 채워야 하며, null 이나 빈 값은 허용되지 않습니다.
8. 최종 출력은 다른 텍스트를 출력하지 말고, **반드시 JSON만** 출력하세요.
⚠️ JSON 외의 설명, 문장, 주석을 절대 출력하지 마세요.

예시 출력:
{{
  "foods": [
    {{"name": "계란후라이", "calories": 150, "protein": 12, "carbs": 1, "fat": 10}},
    {{"name": "삶은 감자", "calories": 120, "protein": 3, "carbs": 26, "fat": 0}}
  ],
  "explanation": "단백질과 탄수화물 균형"
}}
""")


diet_regenerate_day_prompt = ChatPromptTemplate.from_template("""
당신은 개인 맞춤 식단 코치입니다.

[유저 프로필]
{user_profile}

[지난 식단 기록 + 미래 추천 기록]
{history}

[사용 가능한 음식 후보 (DB 기반 Top-K 검색 결과, 최대 20개)]
{foods_context}

---
요구사항:
1. 요청한 날짜({date})의 BREAKFAST, LUNCH, DINNER 세 끼니를 모두 새로 추천하세요.
2. 각 끼니별로 반드시 3~5개의 음식을 추천하세요.
3. 음식은 반드시 위 "음식 후보 리스트"에서만 선택하세요.
4. 각 음식은 JSON 객체로, {{"name": str, "calories": int, "protein": int, "carbs": int, "fat": int}} 형식으로 작성하세요.
5. 유저의 금지 음식이 있다면 절대 포함하지 마세요.
6. 모든 숫자 필드는 반드시 int 또는 float 값으로 채워야 하며 null 은 허용되지 않습니다.
7. 최종 출력은 JSON만 출력하세요. 다른 설명, 문장은 절대 출력하지 마세요.

예시 출력:
{{
  "{date}": {{
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
  }}
}}
""")