"""Application configuration management."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    debug: bool = False

    # Anthropic API
    anthropic_api_key: str

    # Database
    database_url: str = "sqlite+aiosqlite:///./dev_assistant.db"

    # Cache Configuration
    cache_ttl_seconds: int = 3600
    max_cache_size: int = 1000

    # Model Configuration
    default_model: str = "claude-3-5-sonnet-20241022"
    max_tokens: int = 4096
    temperature: float = 0.7

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )


settings = Settings()
