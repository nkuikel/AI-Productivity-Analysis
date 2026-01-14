from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DATABASE_URL: str
    GITHUB_TOKEN: str | None = None
    JOB_SECRET: str | None = None


settings = Settings()
