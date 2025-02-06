from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # careerjet_affid: str
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()