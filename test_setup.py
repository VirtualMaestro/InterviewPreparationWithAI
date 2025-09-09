"""
Simple test to verify project setup
"""
from config import Config
from src.utils.logger import setup_logging


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

    config.OPENAI_API_KEY = "sk-test-key"
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
