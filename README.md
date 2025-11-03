# HelloFit LLM API

이 프로젝트는 사용자의 프로필과 이력을 기반으로 개인화된 식단과 운동 루틴을 추천하는 FastAPI 기반의 LLM API 서버입니다.

### 1. 앱 서버, LLM 서버, 프론트 깃 링크

1. [프론트 깃 링크](https://github.com/yunyami0605/Full-Portfolio)

<br />

2. [앱 서버 깃 링크](https://github.com/yunyami0605/hellofit_server)

<br />

3. [LLM 서버 깃 링크](https://github.com/yunyami0605/hellofit_llm)

### 2. 산출물

1. [헬로핏 프로젝트 기획서 링크](https://cookiejy.notion.site/29e75abb802d808ab2afd94e32524708?source=copy_link)

<br />

2. [시스템 아키텍처 설계서 링크](https://cookiejy.notion.site/29f75abb802d803b8ffedb2a1af0915f?source=copy_link)

<br />

3. [데이터베이스 설계서 링크](https://cookiejy.notion.site/29f75abb802d8006b09dc395b8797c6c?source=copy_link)

<br />

4. [기능 명세서 링크](https://cookiejy.notion.site/29f75abb802d80158670fee0596f4e82?v=29f75abb802d8028b2ab000c5e6efc0d)

<br />

### 2. 주요 기능

- **자동 식단 추천**: 사용자의 건강 정보와 식단 기록을 바탕으로 7일치 식단을 자동으로 생성합니다.
- **식단 재추천**: 특정 날짜의 특정 끼니 또는 하루 전체 식단을 다시 추천받을 수 있습니다.
- **운동 루틴 추천**: 사용자의 목표와 운동 기록에 맞춰 운동 루틴을 생성합니다.
- **운동 설명**: 추천된 특정 운동에 대한 설명을 제공합니다.

### 3. 기술 스택

- **Web Framework**: FastAPI
- **LLM Orchestration**: LangChain
- **LLM Provider**: OpenAI
- **Vector Store**: FAISS (Facebook AI Similarity Search)
- **Dependencies**:
  - `poetry`: 의존성 관리

### 4. 설치 및 설정

1.  **저장소 복제**:

    ```bash
    git clone https://github.com/your-username/hellofit_llm.git
    cd hellofit_llm
    ```

2.  **의존성 설치**:

    ```bash
    poetry install
    ```

3.  **환경 변수 설정**:
    프로젝트 루트 디렉토리에 `.env` 파일을 생성하고 아래 내용을 채워주세요.

    ```env
    # OpenAI
    OPENAI_API_KEY="sk-..."

    # Database
    DB_HOST="your_db_host"
    DB_PORT="your_db_port"
    DB_USER="your_db_user"
    DB_PASSWORD="your_db_password"
    DB_NAME="your_db_name"
    ```

4.  **Vector Store 인덱스 빌드**:
    애플리케이션을 실행하기 전에, 데이터베이스의 음식 정보를 기반으로 FAISS 인덱스를 생성해야 합니다.

    ```bash
    poetry run python scripts/build_index.py
    ```

    이 스크립트는 `faiss_index` 디렉토리에 인덱스 파일을 생성합니다.

5.  실행 방법

아래 명령어를 사용하여 FastAPI 개발 서버를 실행합니다.

```bash
poetry run uvicorn app.main:app --reload --port 8001
```

서버가 실행되면 `http://127.0.0.1:8001/docs`에서 API 문서를 확인할 수 있습니다.

### 5. 프로젝트 구조

```
.
├── app/                    # FastAPI 애플리케이션 소스 코드
│   ├── core/               # 핵심 로직 (설정, 벡터스토어 등)
│   ├── diet/               # 식단 추천 관련 모듈 (라우터, 서비스, 프롬프트)
│   ├── workout/            # 운동 추천 관련 모듈
│   └── main.py             # FastAPI 앱 진입점
├── faiss_index/            # 생성된 FAISS 인덱스 저장 위치
├── scripts/                # 유틸리티 스크립트
│   └── build_index.py      # FAISS 인덱스 생성 스크립트
├── .env.example            # 환경 변수 예시 파일
├── pyproject.toml          # 프로젝트 의존성 및 메타데이터
└── README.md               # 프로젝트 설명 파일
```

### 6. API Endpoints

주요 API 엔드포인트는 다음과 같습니다.

- `GET /health`: 서버 상태 확인

### Diet API (`/recommend/diet`)

- `POST /batch`: 7일치 식단 자동 생성
- `POST /{date}/regenerate`: 특정 날짜/끼니 식단 재성성
- `POST /{date}/regenerate/day`: 특정 날짜 전체 식단 재성성

### Workout API (`/recommend/workout`)

- `POST /manual`: 운동 루틴 수동 생성
- `POST /{date}/regenerate`: 특정 날짜 운동 루틴 재성성
- `GET /{id}/explanation`: 특정 운동 상세 설명 조회
