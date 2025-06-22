from datetime import datetime, timedelta

import pytest
from unittest.mock import patch, MagicMock, AsyncMock

import yaml

from pysentinel.core.scanner import Scanner
from pysentinel.core.threshold import AlertDefinition, Violation, MetricData
from pysentinel.utils.constants import ScannerStatus, Severity


@pytest.fixture
def minimal_config():
    return {
        "global": {"log_level": "INFO"},
        "datasources": {
            "testdb": {"type": "postgresql", "enabled": True, "interval": 60, "config": {"host": "localhost", "port": 5432}},
        },
        "alert_channels": {
            "email1": {"type": "email"}
        },
        "alert_groups": {
            "group1": {
                "enabled": True,
                "alerts": [
                    {
                        "name": "Test Alert",
                        "metrics": "cpu",
                        "query": "SELECT cpu FROM sys",
                        "datasource": "testdb",
                        "threshold": {"max": 90},
                        "severity": "critical",
                        "interval": 60,
                        "alert_channels": ["email1"],
                        "description": "CPU usage high"
                    }
                ]
            }
        }
    }


@patch("pysentinel.core.scanner.load_config", side_effect=lambda x: x)
@patch("pysentinel.core.scanner.PostgreSQLDataSource")
@patch("pysentinel.core.scanner.Email")
def test_scanner_init_and_setup(mock_email, mock_pg, mock_load, minimal_config):
    scanner = Scanner(config=minimal_config)
    assert scanner.status == ScannerStatus.STOPPED
    assert "testdb" in scanner.datasources
    assert "email1" in scanner.alert_channels
    assert len(scanner.alert_definitions) == 1
    assert scanner.alert_definitions[0].name == "Test Alert"


def test_should_send_alert_sets_cooldown():
    scanner = Scanner()
    violation = MagicMock()
    violation.datasource_name = "ds"
    violation.alert_name = "alert"
    # First call should return True, second within cooldown should return False
    assert scanner._should_send_alert(violation) is True
    assert scanner._should_send_alert(violation) is False


@pytest.mark.asyncio
async def test_handle_violation_sends_alert():
    from pysentinel.core.threshold import AlertDefinition

    scanner = Scanner()
    violation = MagicMock(spec=Violation)
    violation.datasource_name = "ds"
    violation.alert_name = "alert"
    violation.violation_id = "ds_alert_1"
    violation.message = "msg"
    scanner._should_send_alert = MagicMock(return_value=True)

    mock_channel = MagicMock()
    mock_channel.send_alert = AsyncMock()
    scanner.alert_channels = {"chan": mock_channel}

    # Use a real AlertDefinition to ensure attribute matching
    alert_def = AlertDefinition(
        name="alert",
        metrics="cpu",
        query="SELECT 1",
        datasource="ds",
        threshold={},
        severity=Severity("critical"),
        interval=60,
        alert_channels=["chan"],
        description="desc"
    )
    scanner.alert_definitions = [alert_def]

    await scanner._handle_violation(violation)
    mock_channel.send_alert.assert_awaited_once()


def test_get_status_and_running():
    scanner = Scanner()
    assert scanner.get_status() == ScannerStatus.STOPPED
    assert scanner.is_running() is False


def test_get_uptime_seconds(monkeypatch):
    scanner = Scanner()
    assert scanner.get_uptime_seconds() == 0
    from datetime import datetime, timedelta
    scanner.start_time = datetime.now() - timedelta(seconds=10)
    assert 9 <= scanner.get_uptime_seconds() <= 11


def test_get_datasources():
    scanner = Scanner()
    scanner.datasources = [
        MagicMock(name="ds1"),
        MagicMock(name="ds2", type="postgresql"),
        MagicMock(name="ds3", type="mysql")
    ]
    datasources = scanner.get_datasources()
    assert len(datasources) == 3
    assert all(isinstance(ds, MagicMock) for ds in datasources)
    assert all(ds.name.startswith("ds") for ds in datasources)
    assert datasources is not None


def test_get_metric_count_async():
    scanner = Scanner()
    scanner._latest_metrics = {
        "ds1": MagicMock(metrics={"a": 1, "b": 2}),
        "ds2": MagicMock(metrics={"c": 3})
    }
    assert scanner.get_metric_count_async() == 3


@pytest.fixture
def config_from_yaml():
    import os
    config_path = os.path.join(os.path.dirname(__file__), "../fixtures/config.yml")
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


def test_scanner_with_fixture_config(config_from_yaml):
    scanner = Scanner(config=config_from_yaml)
    print("Scanner initialized with config:", scanner.alert_channels)
    assert scanner.datasources, "Datasources should be initialized"
    assert scanner.alert_channels, "Alert channels should be initialized"
    assert scanner.alert_definitions, "Alert definitions should be initialized"


@pytest.mark.asyncio
async def test_scan_once_async_handles_no_alerts():
    scanner = Scanner()
    # Provide a dummy alert definition so scan_once_async runs fully
    alert_def = MagicMock(datasource="ds1")
    scanner.alert_definitions = [alert_def]
    scanner.datasources = {"ds1": MagicMock(enabled=True)}
    scanner._should_check_alert = MagicMock(return_value=True)
    scanner._check_alerts_for_datasource = AsyncMock()
    await scanner.scan_once_async()
    assert scanner.last_scan_time is not None


@pytest.mark.asyncio
async def test_scan_once_async_groups_alerts_by_datasource():
    scanner = Scanner()
    alert_def_1 = MagicMock(datasource="ds1")
    alert_def_2 = MagicMock(datasource="ds2")
    alert_def_3 = MagicMock(datasource="ds1")
    scanner.alert_definitions = [alert_def_1, alert_def_2, alert_def_3]
    scanner.datasources = {"ds1": MagicMock(), "ds2": MagicMock()}
    scanner._should_check_alert = MagicMock(return_value=True)
    scanner._check_alerts_for_datasource = AsyncMock()
    await scanner.scan_once_async()
    scanner._check_alerts_for_datasource.assert_any_await("ds1", [alert_def_1, alert_def_3])
    scanner._check_alerts_for_datasource.assert_any_await("ds2", [alert_def_2])


@pytest.mark.asyncio
async def test_scan_once_async_skips_disabled_datasources():
    scanner = Scanner()
    scanner.datasources = {"ds1": MagicMock()}
    scanner.datasources["ds1"].enabled = False
    scanner.datasources["ds1"].interval = 60
    alert_def = MagicMock(datasource="ds1", name="alert1", interval=60)
    scanner.alert_definitions = [alert_def]
    scanner._check_alerts_for_datasource = AsyncMock()
    scanner._alert_db.get_last_run = MagicMock(return_value=None)
    await scanner.scan_once_async()
    scanner._check_alerts_for_datasource.assert_not_awaited()


@pytest.mark.asyncio
async def test_scan_once_async_handles_query_errors():
    scanner = Scanner()
    alert_def = MagicMock(datasource="ds1")
    scanner.alert_definitions = [alert_def]
    datasource = MagicMock(enabled=True, error_count=0, max_errors=3)
    datasource.fetch_data = AsyncMock(side_effect=Exception("Query error"))
    scanner.datasources = {"ds1": datasource}
    scanner._should_check_alert = MagicMock(return_value=True)
    await scanner.scan_once_async()
    assert datasource.error_count == 1
    assert datasource.enabled is True


@pytest.mark.asyncio
async def test_scan_once_async_disables_datasource_after_max_errors():
    scanner = Scanner()
    alert_def = MagicMock(datasource="ds1")
    scanner.alert_definitions = [alert_def]
    datasource = MagicMock(enabled=True, error_count=2, max_errors=3)
    datasource.fetch_data = AsyncMock(side_effect=Exception("Query error"))
    scanner.datasources = {"ds1": datasource}
    scanner._should_check_alert = MagicMock(return_value=True)
    await scanner.scan_once_async()
    assert datasource.error_count == 3
    assert datasource.enabled is False


@pytest.mark.asyncio
async def test_scanner_does_not_send_alert_if_cooldown_active():
    scanner = Scanner()
    violation = MagicMock(spec=Violation)
    violation.datasource_name = "ds"
    violation.alert_name = "alert"
    violation.violation_id = "ds_alert_1"
    violation.message = "msg"
    scanner._should_send_alert = MagicMock(return_value=False)
    mock_channel = MagicMock()
    mock_channel.send_alert = AsyncMock()
    scanner.alert_channels = {"chan": mock_channel}
    from pysentinel.core.threshold import AlertDefinition
    alert_def = AlertDefinition(
        name="alert",
        metrics="cpu",
        query="SELECT 1",
        datasource="ds",
        threshold={},
        severity=Severity("critical"),
        interval=60,
        alert_channels=["chan"],
        description="desc"
    )
    scanner.alert_definitions = [alert_def]
    await scanner._handle_violation(violation)
    mock_channel.send_alert.assert_not_awaited()


def test_scanner_status_methods_return_expected_values():
    scanner = Scanner()
    assert scanner.is_running() is False
    assert scanner.get_status() == ScannerStatus.STOPPED
    scanner._running = True
    assert scanner.is_running() is True


def test_scanner_get_uptime_seconds_returns_zero_if_not_started():
    scanner = Scanner()
    assert scanner.get_uptime_seconds() == 0


def test_scanner_get_uptime_seconds_returns_positive_value():
    scanner = Scanner()
    scanner.start_time = datetime.now() - timedelta(seconds=10)
    assert scanner.get_uptime_seconds() >= 10


def test_scanner_get_last_scan_time_returns_none_initially():
    scanner = Scanner()
    assert scanner.get_last_scan_time() is None


@pytest.mark.asyncio
async def test_scanner_acknowledge_alert_async_acknowledges_violation():
    scanner = Scanner()
    violation = MagicMock(spec=Violation)
    violation.violation_id = "id1"
    violation.acknowledged = False
    scanner._active_violations = {"key": violation}
    result = await scanner.acknowledge_alert_async("id1")
    assert result is True
    assert violation.acknowledged is True


@pytest.mark.asyncio
async def scanner_acknowledge_alert_async_returns_false_for_missing():
    scanner = Scanner()
    scanner._active_violations = {}
    result = await scanner.acknowledge_alert_async("notfound")
    assert result is False


def test_scanner_get_metric_count_async_returns_correct_count():
    scanner = Scanner()
    metric_data1 = MagicMock()
    metric_data1.metrics = {"a": 1, "b": 2}
    metric_data2 = MagicMock()
    metric_data2.metrics = {"c": 3}
    scanner._latest_metrics = {"ds1": metric_data1, "ds2": metric_data2}
    assert scanner.get_metric_count_async() == 3
