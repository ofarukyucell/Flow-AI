from pathlib import Path
from pydantic_settings import BaseSettings,SettingsConfigDict

class Settings(BaseSettings):
    APP_NAME: str
    APP_VERSION: str
    DEBUG: bool

    model_config = SettingsConfigDict(

        env_file=str(Path(__file__).resolve().parents[2]/".env")
    )

settings=Settings()