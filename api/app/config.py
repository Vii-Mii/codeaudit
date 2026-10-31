import json

from pydantic import field_validator
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
    cors_origins: list[str] | str = ["http://localhost:5173"]

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: object) -> list[str]:
        if isinstance(v, str):
            v = v.strip()
            if not v:
                return ["*"]
            if v.startswith("[") and v.endswith("]"):
                try:
                    parsed = json.loads(v)
                    if isinstance(parsed, list):
                        return [str(x) for x in parsed]
                except Exception:
                    pass
                v = v[1:-1]
            return [x.strip().strip("\"'") for x in v.split(",") if x.strip().strip("\"'")]
        if isinstance(v, list):
            return [str(x) for x in v]
        return ["*"]


settings = Settings()
