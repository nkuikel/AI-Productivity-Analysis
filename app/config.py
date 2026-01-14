from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    ENVIRONMENT: str = "local"  #Environment name: local / staging / production

    DATABASE_URL: str | None = None #Database connection string (not used yet)

    GITHUB_TOKEN: str | None = None #placeholder for future Github API Integration

    JOB_SECRET: str | None = None

    class Config:
        env_file = ".env"

settings = Settings()