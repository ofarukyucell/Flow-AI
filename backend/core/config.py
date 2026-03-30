from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str
    APP_VERSION: str
    DEBUG: bool

    # Production'da virgülle ayrılmış origin listesi: "https://app.flowai.com,https://flowai.com"
    CORS_ORIGINS: str = "*"

    @property
    def allowed_origins(self) -> List[str]:
        if self.CORS_ORIGINS == "*":
            return ["*"]
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).resolve().parents[2] / ".env")
    )


settings = Settings()