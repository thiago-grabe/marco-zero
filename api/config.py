from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5490/marco_zero_dev"
    jwt_secret: str = "marco-zero-dev-secret-change-in-production"
    openai_api_key: str = ""
    environment: str = "development"
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:5174", "http://localhost:3000"]

    @property
    def is_dev(self) -> bool:
        return self.environment == "development"


settings = Settings()
