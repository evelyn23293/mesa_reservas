from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    api_key: str = "supersecretkey"
    database_url: str = "sqlite:///./database.db"

    class Config:
        env_file = ".env"

settings = Settings()