import pytest
import tempfile
import os
import json
import yaml
from pysentinel.config.loader import load_config
from pysentinel.utils.exception import ScannerException


def test_load_config_from_dict():
    config = {"a": 1, "b": 2}
    result = load_config(config)
    assert result == config


def test_load_config_from_json_file():
    data = {"foo": "bar"}
    with tempfile.NamedTemporaryFile(mode="w+", suffix=".json", delete=False) as f:
        json.dump(data, f)
        f.flush()
        f.seek(0)
        result = load_config(f.name)
    os.unlink(f.name)
    assert result == data


def test_load_config_from_yaml_file():
    data = {"foo": "bar"}
    with tempfile.NamedTemporaryFile(mode="w+", suffix=".yaml", delete=False) as f:
        yaml.dump(data, f)
        f.flush()
        f.seek(0)
        result = load_config(f.name)
    os.unlink(f.name)
    assert result == data


def test_load_config_raises_scanner_exception_on_invalid_file():
    with pytest.raises(ScannerException):
        load_config("nonexistent_file.json")


def test_load_config_raises_scanner_exception_on_invalid_content():
    with tempfile.NamedTemporaryFile(mode="w+", suffix=".json", delete=False) as f:
        f.write("not a json")
        f.flush()
        f.seek(0)
        with pytest.raises(ScannerException):
            load_config(f.name)
    os.unlink(f.name)
