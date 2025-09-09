"""
Test configuration management
"""
from config import Config
import sys
from pathlib import Path

# Add project root to path for imports
sys.path.append(str(Path(__file__).parent.parent))


def test_config_initialization():
    """Test that Config initializes with default values"""
    config = Config()

    assert config.APP_NAME == "AI Interview Prep Assistant"
    assert config.VERSION == "1.0.0"
    assert config.DEFAULT_MODEL == "gpt-4o"
    assert config.MAX_TOKENS == 2000
    assert config.DEFAULT_TEMPERATURE == 0.7
    assert config.MAX_QUESTIONS == 20
    assert config.DEFAULT_QUESTIONS == 5


def test_config_directories_created():
    """Test that required directories are created"""
    config = Config()
    config.__post_init__()

    assert config.LOGS_DIR.exists()
    assert config.EXPORTS_DIR.exists()


def test_config_to_dict():
    """Test configuration dictionary conversion"""
    config = Config()
    config_dict = config.to_dict()

    # Should include non-sensitive data
    assert "APP_NAME" in config_dict
    assert "VERSION" in config_dict

    # Should exclude sensitive data
    assert "OPENAI_API_KEY" not in config_dict


def test_config_validation():
    """Test configuration validation"""
    config = Config()

    # Should fail with empty or default API key
    assert not config.validate()

    # Should fail with invalid format
    config.OPENAI_API_KEY = "invalid-key"
    assert not config.validate()

    # Should pass with valid format
    config.OPENAI_API_KEY = "sk-test-key-123"
    assert config.validate()
