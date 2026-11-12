"""Application configuration loaded from environment variables."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Central configuration. Every value can be overridden via .env or shell env."""

    database_url: str = "sqlite:///./milya_scribe.db"
    groq_api_key: str = ""
    llm_model: str = "qwen/qwen3.8-27b"
    stt_model: str = "whisper-large-v3-turbo"
    secret_key: str = "dev-secret-change-in-production"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
