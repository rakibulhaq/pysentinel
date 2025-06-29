import pytest
from datetime import datetime, timedelta
from pysentinel.core.threshold import Violation, MetricData, AlertDefinition
from pysentinel.utils.constants import Severity


class TestThreshold:
    def test_violation_creation_and_to_dict(self):
        now = datetime.now()
        v = Violation(
            alert_name="CPU High",
            metric_name="cpu_usage",
            current_value=95,
            threshold_value=90,
            operator=">",
            severity=Severity.CRITICAL,
            message="CPU usage is too high",
            timestamp=now,
            datasource_name="server1",
        )
        d = v.to_dict()
        assert d["alert_name"] == "CPU High"
        assert d["severity"] == Severity.CRITICAL.value
        assert d["timestamp"] == now.isoformat()
        assert v.violation_id.startswith("server1_CPU High_")

    def test_metric_data_to_dict(self):
        now = datetime.now()
        m = MetricData(
            datasource_name="db1",
            metrics={"connections": 10},
            timestamp=now,
            collection_time_ms=123.4,
        )
        d = m.to_dict()
        assert d["datasource_name"] == "db1"
        assert d["metrics"]["connections"] == 10
        assert d["timestamp"] == now.isoformat()
        assert d["collection_time_ms"] == 123.4

    def test_alert_definition_create_violation(self):
        ad = AlertDefinition(
            name="Memory Low",
            metrics="mem_free",
            query="SELECT mem_free FROM sys",
            datasource="server2",
            threshold={"min": 100},
            severity=Severity.WARNING,
            interval=60,
            alert_channels=["email"],
            description="Memory is low",
        )
        v = ad.create_violation(current_value=80, datasource_name="server2")
        assert isinstance(v, Violation)
        assert v.operator == ">="
        assert v.threshold_value == 100
        assert v.current_value == 80
        assert v.severity == Severity.WARNING

    def test_alert_definition_check_threshold_max(self):
        ad = AlertDefinition(
            name="Disk Full",
            metrics="disk_usage",
            query="SELECT disk_usage FROM sys",
            datasource="server3",
            threshold={"max": 80},
            severity=Severity.CRITICAL,
            interval=60,
            alert_channels=["slack"],
            description="Disk usage is high",
        )
        assert ad.check_threshold(85) is True
        assert ad.check_threshold(75) is False

    def test_alert_definition_check_threshold_min(self):
        ad = AlertDefinition(
            name="Temp Low",
            metrics="temp",
            query="SELECT temp FROM sys",
            datasource="server4",
            threshold={"min": 10},
            severity=Severity.WARNING,
            interval=60,
            alert_channels=["telegram"],
            description="Temperature is low",
        )
        assert ad.check_threshold(5) is True
        assert ad.check_threshold(15) is False

    def test_alert_definition_check_threshold_invalid(self):
        ad = AlertDefinition(
            name="Invalid",
            metrics="invalid",
            query="SELECT invalid FROM sys",
            datasource="server5",
            threshold={},
            severity=Severity.INFO,
            interval=60,
            alert_channels=[],
            description="No threshold",
        )
        assert ad.check_threshold("not_a_number") is False
        assert ad.check_threshold(None) is False
