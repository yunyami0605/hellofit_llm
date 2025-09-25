from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "HelloFit LLM API"
    app_version: str = "0.1.0"
    environment: str = "local"

    # OpenAI
    openai_api_key: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
