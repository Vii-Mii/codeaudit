from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="CODEAUDIT_", env_file=".env")

    database_url: str = "postgresql+psycopg://codeaudit:codeaudit@db:5432/codeaudit"
    redis_url: str = "redis://redis:6379/0"
    # Server-side token for public data; a fine-grained token with no extra scopes is enough.
    github_token: str = ""
    cache_ttl_seconds: int = 3600
    github_client_id: str = ""
    github_client_secret: str = ""
    cors_origins: list[str] = ["http://localhost:5173"]


settings = Settings()
