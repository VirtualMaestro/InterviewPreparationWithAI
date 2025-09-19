"""
Simple test to verify project setup
"""
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import sys
from pathlib import Path

from src.utils.logger import setup_logging

from src.config import Config

# Add src to path BEFORE imports


def test_config():
    """Test configuration setup"""
    print("Testing configuration...")

    config = Config()
    print(f"✓ Config initialized: {config.APP_NAME} v{config.VERSION}")

    # Test directory creation
    config.__post_init__()
    print(
        f"✓ Directories created: {config.LOGS_DIR.exists()}, {config.EXPORTS_DIR.exists()}")

    # Test validation
    print(f"✓ Validation (should fail): {config.validate()}")

    config.openai_api_key = "sk-test-key"
    print(f"✓ Validation (should pass): {config.validate()}")

    print("Configuration test passed!")


def test_logging():
    """Test logging setup"""
    print("\nTesting logging...")

    logger = setup_logging()
    logger.info("Test log message")
    print("✓ Logger initialized successfully")

    print("Logging test passed!")


if __name__ == "__main__":
    test_config()
    test_logging()
    print("\n🎉 All setup tests passed! Project structure is ready.")
