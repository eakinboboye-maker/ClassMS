from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Class Management Backend"
    DATABASE_URL: str = "sqlite:///./app.db"
    SECRET_KEY: str = "change-me"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    REDIS_URL: str = "redis://localhost:6379/0"

    AI_GRADING_ENABLED: bool = True
    AI_PROVIDER: str = "mock"
    AI_MODEL: str = "gpt-5"
    AI_GRADING_REVIEW_REQUIRED: bool = True
    OPENAI_API_KEY: str | None = None

    SEB_REQUIRED_FOR_FORMAL_EXAMS: bool = True

    CORS_ORIGINS: str = "http://localhost:3001,http://localhost:3002"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_origins_list(self) -> list[str]:
        return [x.strip() for x in self.CORS_ORIGINS.split(',') if x.strip()]


settings = Settings()
