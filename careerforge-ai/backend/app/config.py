from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/careerforge"
    GEMINI_API_KEY: str = "your_gemini_api_key_here"
    JWT_SECRET: str = "your_jwt_secret_here"
    ENVIRONMENT: str = "development"

    class Config:
        env_file = ".env"

settings = Settings()
