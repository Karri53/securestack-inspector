# backend/app/core/config.py
"""
All app configuration lives here, loaded from environment variables.

We use pydantic-settings instead of `os.getenv("FOO")` scattered everywhere
because it validates types at startup. If POSTGRES_PORT isn't actually
an integer, the app refuses to boot — better than a cryptic crash three
hours into a scan when we finally try to use it.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # ---- Postgres ----
    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_host: str = "postgres"  # default = the Docker service name
    postgres_port: int = 5432

    # ---- Redis ----
    redis_host: str = "redis"
    redis_port: int = 6379

    # ---- API ----
    api_env: str = "development"
    api_secret_key: str
    log_level: str = "INFO"

    # Tell pydantic where to look for env vars. In Docker, they come from
    # docker-compose env_file. Running outside Docker (e.g. local tests),
    # it falls back to reading .env directly.
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)

    @property
    def database_url(self) -> str:
        """Build the SQLAlchemy connection string from the individual pieces."""
        return (
            f"postgresql+psycopg2://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


# Singleton — import `settings` everywhere config is needed.
# Pydantic reads env vars once at startup; this object stays constant after.
settings = Settings()