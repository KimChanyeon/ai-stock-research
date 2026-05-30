from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    google_api_key: str
    # crewAI LLM model (provider/model-name 형식)
    gemini_model: str = "gemini/gemini-2.0-flash"
    # google-genai SDK용 모델 (검색 grounding 전용, 프로바이더 접두사 제외)
    gemini_search_model: str = "gemini-2.0-flash"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}


settings = Settings()
