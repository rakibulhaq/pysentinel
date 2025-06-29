import pytest
import asyncio
from pathlib import Path


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def sample_config():
    """Sample configuration for tests"""
    return {
        "scanner": {"interval": 30, "timeout": 10},
        "alerts": {"email": {"enabled": True, "smtp_server": "smtp.example.com"}},
    }


@pytest.fixture
def temp_config_file(tmp_path, sample_config):
    """Create temporary config file for tests"""
    config_file = tmp_path / "test_config.yml"
    import yaml

    config_file.write_text(yaml.dump(sample_config))
    return config_file
