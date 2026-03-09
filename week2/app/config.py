from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel, ConfigDict, Field

load_dotenv()

BASE_DIR = Path(__file__).resolve().parents[1]
DEFAULT_FRONTEND_DIR = BASE_DIR / "frontend"
DEFAULT_DATA_DIR = BASE_DIR / "data"


class Settings(BaseModel):
    model_config = ConfigDict(frozen=True)

    app_title: str = Field(default_factory=lambda: os.getenv("APP_TITLE", "Action Item Extractor"))
    frontend_dir: Path = Field(default=DEFAULT_FRONTEND_DIR)
    db_path: Path = Field(
        default_factory=lambda: Path(os.getenv("WEEK2_DB_PATH", DEFAULT_DATA_DIR / "app.db"))
    )
    ollama_model: str = Field(default_factory=lambda: os.getenv("OLLAMA_MODEL", "llama3.1:8b"))
    ollama_host: str = Field(
        default_factory=lambda: os.getenv("OLLAMA_HOST", "http://127.0.0.1:8112")
    )

    @property
    def data_dir(self) -> Path:
        return self.db_path.parent


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
