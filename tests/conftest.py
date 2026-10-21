import pytest


@pytest.fixture(autouse=True)
def isolated_cwd(tmp_path, monkeypatch):
    """Run each test in its own directory so files the scanner writes relative
    to the CWD (e.g. alerts.db) never leak between tests or into the repo"""
    monkeypatch.chdir(tmp_path)
    return tmp_path


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
