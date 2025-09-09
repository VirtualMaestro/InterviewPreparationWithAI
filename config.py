"""
Application configuration management
"""
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict


@dataclass
class Config:
    """Centralized configuration management"""

    # API Configuration
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    DEFAULT_MODEL: str = "gpt-4o"
    MAX_TOKENS: int = 2000
    DEFAULT_TEMPERATURE: float = 0.7

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

    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary (excluding sensitive data)"""
        return {
            k: v for k, v in self.__dict__.items()
            if not k.startswith("_") and k != "OPENAI_API_KEY"
        }

    def validate(self) -> bool:
        """Validate configuration settings"""
        if not self.OPENAI_API_KEY or self.OPENAI_API_KEY == "sk-your-actual-api-key-here":
            return False

        if not self.OPENAI_API_KEY.startswith("sk-"):
            return False

        return True
