from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",  # 알 수 없는 환경변수는 무시
    )
    app_name: str = "HelloFit LLM API"
    app_version: str = "0.1.0"
    environment: str = "local"

    # OpenAI
    openai_api_key: Optional[str] = None
    # Optional: 서비스 간 인증용 API 키 (스프링 → LLM 서버)
    service_api_key: Optional[str] = None


settings = Settings()
