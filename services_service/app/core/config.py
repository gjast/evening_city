from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    APP_NAME: str = "Services Service"
    DEBUG: bool = True
    
    DB_HOST: str = "services_postgres"
    DB_PORT: int = 5432
    DB_USER: str = "niro"
    DB_PASSWORD: str = "niro"
    DB_NAME: str = "evening_city"
    
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

