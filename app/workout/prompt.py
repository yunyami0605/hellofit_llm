from langchain.prompts import ChatPromptTemplate

# 운동 추천 프롬프트
workout_recommend_prompt = ChatPromptTemplate.from_template("""
당신은 개인 맞춤 운동 코치입니다.

[유저 프로필]
{user_profile}

[최근 운동 기록]
{workout_history}

---
요구사항:
1. 오늘 운동 루틴을 2~5개 추천하세요.
2. 각 운동에 운동명, 세트 수, 반복 횟수(repetitions) 또는 시간(duration_minutes), 칼로리 소모량을 포함하세요.
3. JSON 형식으로 반환하세요:

{{
  "exercises": [
    {{"name": "푸시업", "sets": 3, "repetitions": 15, "calories_burned": 100}},
    {{"name": "스쿼트", "sets": 3, "repetitions": 20, "calories_burned": 120}},
    {{"name": "플랭크", "duration_minutes": 3, "calories_burned": 50}}
  ],
  "explanation": "추천 이유를 한국어로 간단히 설명"
}}
""")
