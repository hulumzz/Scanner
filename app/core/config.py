from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')
    app_name: str = 'KK Scanner'
    environment: str = Field('development', alias='APP_ENV')
    database_url: str = Field('sqlite:///./kk_scanner.db', alias='DATABASE_URL')
    secret_key: str = Field('change-me-in-production', alias='SECRET_KEY')
    admin_username: str = Field('admin', alias='APP_ADMIN_USERNAME')
    admin_password: str = Field('admin', alias='APP_ADMIN_PASSWORD')
    vision_provider: str = Field('groq', alias='VISION_PROVIDER')
    vision_model: str = Field('qwen/qwen3.8-27b', alias='VISION_MODEL')
    groq_api_key: str | None = Field(None, alias='GROQ_API_KEY')
    gemini_api_key: str | None = Field(None, alias='GEMINI_API_KEY')
    ai_timeout_seconds: float = Field(45.0, alias='AI_TIMEOUT_SECONDS')
    max_upload_bytes: int = Field(4 * 1024 * 1024, alias='MAX_UPLOAD_BYTES')
    max_batch_items: int = Field(20, alias='MAX_BATCH_ITEMS')
    min_effective_width: int = Field(1600, alias='MIN_EFFECTIVE_WIDTH')
    thumbnail_long_edge: int = Field(360, alias='THUMBNAIL_LONG_EDGE')
    login_rate_limit_per_minute: int = 10
    api_rate_limit_per_minute: int = 120

    @property
    def is_production(self) -> bool:
        return self.environment.lower() == 'production'


@lru_cache
def get_settings() -> Settings:
    return Settings()
