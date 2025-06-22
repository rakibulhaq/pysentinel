from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Any, Dict, List, Optional

from pysentinel.utils.constants import Severity


@dataclass
class Violation:
    """Represents a threshold violation"""
    alert_name: str
    metric_name: str
    current_value: Any
    threshold_value: Any
    operator: str
    severity: Severity
    message: str
    timestamp: datetime
    datasource_name: str
    alert_group: str = None
    violation_id: str = None
    acknowledged: bool = False

    def __post_init__(self):
        if not self.violation_id:
            self.violation_id = f"{self.datasource_name}_{self.alert_name}_{int(self.timestamp.timestamp())}"

    def to_dict(self) -> Dict:
        data = asdict(self)
        data['severity'] = self.severity.value
        data['timestamp'] = self.timestamp.isoformat()
        return data


@dataclass
class MetricData:
    """Represents collected metric data"""
    datasource_name: str
    metrics: Dict[str, Any]
    timestamp: datetime
    collection_time_ms: float = 0

    def to_dict(self) -> Dict:
        return {
            'datasource_name': self.datasource_name,
            'metrics': self.metrics,
            'timestamp': self.timestamp.isoformat(),
            'collection_time_ms': self.collection_time_ms
        }


@dataclass
class AlertDefinition:
    """Represents an alert definition from config"""
    name: str
    metrics: str
    query: str
    datasource: str
    threshold: Dict[str, Any]
    severity: Severity
    interval: int
    alert_channels: List[str]
    description: str
    alert_group: str = None
    enabled: bool = True

    def create_violation(self, current_value: Any, datasource_name: str) -> Violation:
        """Create a violation from this alert definition"""
        threshold_value = self.threshold.get('max') or self.threshold.get('min')
        operator = '<=' if self.threshold.get('max') else '>='

        return Violation(
            alert_name=self.name,
            metric_name=self.metrics,
            current_value=current_value,
            threshold_value=threshold_value,
            operator=operator,
            severity=self.severity,
            message=self.description,
            timestamp=datetime.now(),
            datasource_name=datasource_name,
            alert_group=self.alert_group
        )

    def check_threshold(self, value: Any) -> bool:
        """Check if a value violates this alert's threshold"""
        try:
            if self.threshold.get('max') is not None:
                return float(value) > float(self.threshold['max'])
            elif self.threshold.get('min') is not None:
                return float(value) < float(self.threshold['min'])
            return False
        except (ValueError, TypeError):
            return False


class Threshold:
    """
    Represents a threshold for alerting.
    """
    def __init__(self, metric_name: str, operator: str, value: float, severity: Severity = Severity.WARNING,
                 message: str = "", datasource_filter: Optional[str] = None):
        self.metric_name = metric_name
        self.operator = operator
        self.value = value
        self.severity = severity
        self.message = message
        self.datasource_filter = datasource_filter

    def __repr__(self):
        return f"Threshold(metric={self.metric_name}, operator={self.operator}, value={self.value})"
