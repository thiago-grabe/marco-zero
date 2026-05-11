from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/marco_zero_dev"
    supabase_jwt_secret: str = ""
    openai_api_key: str = ""
    environment: str = "development"
    cors_origins: list[str] = ["http://localhost:5173"]

    @property
    def is_dev(self) -> bool:
        return self.environment == "development"


settings = Settings()
