"""
Application configuration management
"""
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from src.models.enums import AIModel


@dataclass
class Config:
    """Centralized configuration management"""

    # API Configuration
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    model: str = AIModel.GPT_5.value
    max_tokens: int = 2000
    temperature: float = 0.7
    top_p: float = 0.9

    # Application Settings
    APP_NAME: str = "AI Interview Prep Assistant"
    VERSION: str = "1.0.0"
    DEBUG_MODE: bool = os.getenv("DEBUG", "false").lower() == "true"

    # Security Settings
    MAX_INPUT_LENGTH: int = int(os.getenv("MAX_INPUT_LENGTH", "5000"))
    MIN_INPUT_LENGTH: int = 10
    RATE_LIMIT_CALLS: int = int(
        os.getenv("RATE_LIMIT_CALLS", "100"))  # per hour

    # UI Settings
    MAX_QUESTIONS: int = 20
    DEFAULT_QUESTIONS: int = 5
    SESSION_HISTORY_LIMIT: int = 10

    # File Paths
    PROJECT_ROOT: Path = Path(__file__).parent
    LOGS_DIR: Path = PROJECT_ROOT / "logs"
    EXPORTS_DIR: Path = PROJECT_ROOT / "exports"

    def __post_init__(self):
        """Create necessary directories"""
        self.LOGS_DIR.mkdir(exist_ok=True)
        self.EXPORTS_DIR.mkdir(exist_ok=True)

    def to_dict(self) -> dict[str, Any]:
        """Convert config to dictionary (excluding sensitive data)"""
        return {
            k: v for k, v in self.__dict__.items()
            if not k.startswith("_") and k != "OPENAI_API_KEY"
        }

    def validate(self) -> bool:
        """Validate configuration settings"""
        if not self.openai_api_key or self.openai_api_key == "sk-your-actual-api-key-here":
            return False

        if not self.openai_api_key.startswith("sk-"):
            return False

        return True
