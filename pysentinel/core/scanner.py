import asyncio
import logging
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from typing import Dict, Union, List, Callable, Optional

from pysentinel.config.loader import load_config
from pysentinel.core.threshold import MetricData, Violation, AlertDefinition, Threshold
from pysentinel.datasources.api import HTTPDataSource
from pysentinel.datasources.base import DataSource
from pysentinel.datasources.database import PostgreSQLDataSource
from pysentinel.datasources.elasticsearch import ElasticsearchDataSource
from pysentinel.datasources.prometheus import PrometheusDataSource
from pysentinel.datasources.redis import RedisDataSource
from pysentinel.channels import Email, Slack, Webhook, Telegram
from pysentinel.channels.base import AlertChannel
from pysentinel.utils.constants import Severity, ScannerStatus
from pysentinel.utils.exception import DataSourceException, ThresholdException
from pysentinel.utils.alert_db import AlertDB

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Scanner:
    """
    Scanner class to handle scanning operations.
    """

    def __init__(self, config: Union[str, Dict] = None):
        self.status = ScannerStatus.STOPPED
        self.datasources: Dict[str, DataSource] = {}
        self.alert_channels: Dict[str, AlertChannel] = {}
        self.alert_groups: Dict[str, Dict] = {}
        self.alert_definitions: List[AlertDefinition] = []

        # Internal state
        self._running = False
        self._scan_task = None
        self._executor = ThreadPoolExecutor(max_workers=10)
        self.start_time = None
        self.last_scan_time = None
        self.thresholds: List[Threshold] = []
        self._alert_db = AlertDB()

        # Metrics and violations storage
        self._latest_metrics: Dict[str, MetricData] = {}
        self._active_violations: Dict[str, Violation] = {}
        self._violation_history: List[Violation] = []
        self._max_history = 1000

        # Alert cooldown tracking
        self._alert_cooldowns: Dict[str, datetime] = {}

        # Callbacks
        self._violation_callbacks: List[Callable[[Violation], None]] = []
        self._data_callbacks: List[Callable[[MetricData], MetricData]] = []

        # Configuration
        self._config = {}
        self._global_config = {}

        if config:
            self._config = load_config(config)
            self._setup_from_config()

    def _setup_from_config(self):
        """Setup scanner components from configuration"""
        config = self._config

        # Setup global configuration
        self._global_config = config.get('global', {})

        # Setup data sources
        self._setup_datasources(config.get('datasources', {}))

        # Setup alert channels
        self._setup_channels(config.get('alert_channels', {}))

        # Setup alert groups and their alerts
        self._setup_alert_groups(config.get('alert_groups', {}))

    def _setup_datasources(self, datasources_config: Dict):
        """Setup data sources from configuration"""
        datasource_factories = {
            'postgresql': PostgreSQLDataSource,
            'http': HTTPDataSource,
            'redis': RedisDataSource,
            'prometheus': PrometheusDataSource,
            'elasticsearch': ElasticsearchDataSource
        }

        for name, config in datasources_config.items():
            ds_type = config.get('type')
            ds_enabled = config.get('enabled', False)

            if ds_type in datasource_factories and ds_enabled:
                try:
                    datasource = datasource_factories[ds_type](name, config)
                    self.datasources[name] = datasource
                    logger.info(f"Added {ds_type} datasource: {name}")
                except Exception as e:
                    logger.error(f"Failed to create datasource {name}: {e}")
            else:
                logger.warning(f"Unknown datasource type: {ds_type}")

    def _setup_channels(self, channel_config: Dict):
        """Setup alert channels from configuration"""
        channel_factory = {
            'email': Email,
            'slack': Slack,
            'webhook': Webhook,
            'telegram': Telegram
        }

        for name, config in channel_config.items():
            channel_type = config.get('type')
            if channel_type in channel_factory:
                try:
                    channel = channel_factory[channel_type](name, config)
                    self.alert_channels[name] = channel
                    logger.info(f"Added {channel_type} alert channel: {name}")
                except Exception as e:
                    logger.error(f"Failed to create alert channel {name}: {e}")
            else:
                logger.warning(f"Unknown alert channel type: {channel_type}")

    def _setup_alert_groups(self, alert_groups_config: Dict):
        """Setup alert groups and their alerts from configuration"""
        for group_name, group_config in alert_groups_config.items():
            if not group_config.get('enabled', True):
                continue

            self.alert_groups[group_name] = group_config

            # Setup alerts within this group
            for alert_config in group_config.get('alerts', []):
                try:
                    alert_def = AlertDefinition(
                        name=alert_config['name'],
                        metrics=alert_config['metrics'],
                        query=alert_config['query'],
                        datasource=alert_config['datasource'],
                        threshold=alert_config['threshold'],
                        severity=Severity(alert_config['severity']),
                        interval=alert_config['interval'],
                        alert_channels=alert_config['alert_channels'],
                        description=alert_config['description'],
                        alert_group=group_name
                    )
                    self.alert_definitions.append(alert_def)
                    logger.info(f"Added alert '{alert_def.name}' to group '{group_name}'")
                except Exception as e:
                    logger.error(f"Failed to create alert {alert_config.get('name')}: {e}")

    def _should_send_alert(self, violation: Violation) -> bool:
        """Check if alert should be sent based on cooldown"""
        cooldown_minutes = self._global_config.get('alert_cooldown_minutes', 5)
        cooldown_key = f"{violation.datasource_name}_{violation.alert_name}"

        if cooldown_key in self._alert_cooldowns:
            time_since_last = datetime.now() - self._alert_cooldowns[cooldown_key]
            if time_since_last.total_seconds() < cooldown_minutes * 60:
                return False

        self._alert_cooldowns[cooldown_key] = datetime.now()
        return True

    async def start_async(self):
        """Start the scanner asynchronously"""
        if self._running:
            logger.warning("Scanner is already running")
            return

        self.status = ScannerStatus.RUNNING
        self._running = True
        self.start_time = datetime.now()

        logger.info("Starting PySentinel scanner with alert groups...")

        # Start the main scan loop
        self._scan_task = asyncio.create_task(self._scan_loop())

        logger.info("Scanner started successfully")

    def start(self):
        """Start the scanner (blocking)"""
        asyncio.run(self._start_and_wait())

    async def _start_and_wait(self):
        """Helper method for blocking start"""
        await self.start_async()
        try:
            await self._scan_task
        except KeyboardInterrupt:
            logger.info("Received interrupt signal")
        finally:
            await self.stop_async()

    def start_background(self):
        """Start the scanner in a background thread"""

        def run_scanner():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self._start_and_wait())

        thread = threading.Thread(target=run_scanner, daemon=True)
        thread.start()
        return thread

    async def stop_async(self):
        """Stop the scanner asynchronously"""
        if not self._running:
            return

        logger.info("Stopping scanner...")
        self._running = False
        self.status = ScannerStatus.STOPPED

        if self._scan_task:
            self._scan_task.cancel()
            try:
                await self._scan_task
            except asyncio.CancelledError:
                pass

        # Close all data sources
        for datasource in self.datasources.values():
            try:
                await datasource.close()
            except Exception as e:
                logger.error(f"Error closing data source {datasource.name}: {e}")

        self._executor.shutdown(wait=True)
        logger.info("Scanner stopped")

    async def _scan_loop(self):
        """Main scanning loop"""
        while self._running:
            try:
                await self.scan_once_async()
                await asyncio.sleep(1)  # Small delay between checks
            except Exception as e:
                logger.error(f"Error in scan loop: {e}")
                self.status = ScannerStatus.ERROR
                await asyncio.sleep(5)  # Wait before retrying
                if self._running:
                    self.status = ScannerStatus.RUNNING

    async def scan_once_async(self):
        """Perform a single scan cycle asynchronously"""
        scan_start = time.time()

        # Check which alerts need to be evaluated
        current_time = datetime.now()
        alerts_to_check = []

        for alert_def in self.alert_definitions:
            # Check if it's time to evaluate this alert
            if self._should_check_alert(alert_def, current_time):
                alerts_to_check.append(alert_def)

        if not alerts_to_check:
            return

        # Group alerts by datasource to minimize queries
        alerts_by_datasource = {}
        for alert_def in alerts_to_check:
            if alert_def.datasource not in alerts_by_datasource:
                alerts_by_datasource[alert_def.datasource] = []
            alerts_by_datasource[alert_def.datasource].append(alert_def)

        # Execute queries for each datasource
        tasks = []
        for datasource_name, alerts in alerts_by_datasource.items():
            # Check if the datasource is enabled and exists
            if datasource_name not in self.datasources:
                logger.warning(f"Datasource '{datasource_name}' not found, skipping alerts")
                continue
            if not self.datasources[datasource_name].enabled:
                logger.warning(f"Datasource '{datasource_name}' is disabled, skipping alerts")
                continue

            if datasource_name in self.datasources:
                task = asyncio.create_task(
                    self._check_alerts_for_datasource(datasource_name, alerts)
                )
                tasks.append(task)

        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

        self.last_scan_time = datetime.now()
        scan_duration = time.time() - scan_start
        logger.debug(f"Scan completed in {scan_duration:.2f}s")

    def _should_check_alert(self, alert_def: AlertDefinition, current_time: datetime) -> bool:
        """Check if an alert should be evaluated based on its interval"""
        if not alert_def.enabled:
            return False
        if alert_def.interval <= 0:
            return True
        last_run = self._alert_db.get_last_run(alert_def.name)
        if not last_run or (current_time - last_run).total_seconds() >= alert_def.interval:
            return True
        return False

    async def _check_alerts_for_datasource(self, datasource_name: str, alerts: List[AlertDefinition]):
        """Check all alerts for a specific datasource"""
        datasource = self.datasources[datasource_name]

        if not datasource.enabled:
            return

        for alert_def in alerts:
            try:
                # Execute the query
                result = await datasource.fetch_data(alert_def.query)

                # Check if the metric exists in the result
                if alert_def.metrics in result:
                    metric_value = result[alert_def.metrics]

                    # Check threshold
                    if alert_def.check_threshold(metric_value):
                        violation = alert_def.create_violation(metric_value, datasource_name)
                        await self._handle_violation(violation)
                    else:
                        # Clear any existing violation for this alert
                        violation_key = f"{datasource_name}_{alert_def.name}"
                        if violation_key in self._active_violations:
                            del self._active_violations[violation_key]

                # Store metrics
                metric_data = MetricData(
                    datasource_name=datasource_name,
                    metrics=result,
                    timestamp=datetime.now()
                )
                self._latest_metrics[datasource_name] = metric_data

            except Exception as e:
                logger.error(f"Error checking alert '{alert_def.name}' on datasource '{datasource_name}': {e}")
                datasource.error_count += 1

                if datasource.error_count >= datasource.max_errors:
                    logger.error(f"Disabling datasource {datasource_name} due to too many errors")
                    datasource.enabled = False

    async def _handle_violation(self, violation: Violation):
        """Handle a threshold violation"""
        # Check if we should send this alert (cooldown)
        if not self._should_send_alert(violation):
            return

        # Store active violation
        violation_key = f"{violation.datasource_name}_{violation.alert_name}"
        self._active_violations[violation_key] = violation

        # Add to history
        self._violation_history.append(violation)
        if len(self._violation_history) > self._max_history:
            self._violation_history.pop(0)

        logger.warning(f"Alert triggered: {violation.alert_name} - {violation.message}")

        # Execute violation callbacks
        for callback in self._violation_callbacks:
            try:
                callback(violation)
            except Exception as e:
                logger.error(f"Error in violation callback: {e}")

        # Send alerts to configured channels
        alert_def = next((a for a in self.alert_definitions if a.name == violation.alert_name), None)
        if alert_def:
            for channel_name in alert_def.alert_channels:
                if channel_name in self.alert_channels:
                    try:
                        await self.alert_channels[channel_name].send_alert(violation)
                    except Exception as e:
                        logger.error(f"Error sending alert via {channel_name}: {e}")

    # Status and information methods
    def is_running(self) -> bool:
        """Check if scanner is running"""
        return self._running

    def get_status(self) -> ScannerStatus:
        """Get current scanner status"""
        return self.status

    def get_uptime_seconds(self) -> float:
        """Get scanner uptime in seconds"""
        if self.start_time:
            return (datetime.now() - self.start_time).total_seconds()
        return 0

    def get_last_scan_time(self) -> Optional[datetime]:
        """Get timestamp of last scan"""
        return self.last_scan_time

    async def get_latest_metrics_async(self) -> Dict[str, Dict]:
        """Get latest metrics from all data sources"""
        return {name: data.to_dict() for name, data in self._latest_metrics.items()}

    def get_latest_metrics(self) -> Dict[str, Dict]:
        """Get latest metrics (sync version)"""
        return asyncio.run(self.get_latest_metrics_async())

    async def get_metrics_by_source_async(self, datasource_name: str) -> Optional[Dict]:
        """Get latest metrics from specific data source"""
        metric_data = self._latest_metrics.get(datasource_name)
        return metric_data.to_dict() if metric_data else None

    async def get_active_alerts_async(self) -> List[Dict]:
        """Get currently active alerts"""
        return [violation.to_dict() for violation in self._active_violations.values()]

    async def get_alert_history_async(self, limit: int = 100) -> List[Dict]:
        """Get alert history"""
        recent_violations = self._violation_history[-limit:] if limit else self._violation_history
        return [violation.to_dict() for violation in recent_violations]

    async def acknowledge_alert_async(self, alert_id: str) -> bool:
        """Acknowledge an alert"""
        for violation in self._active_violations.values():
            if violation.violation_id == alert_id:
                violation.acknowledged = True
                logger.info(f"Alert {alert_id} acknowledged")
                return True
        return False

    def get_datasources(self) -> List[str]:
        """Get list of data source names"""
        return [ds.name for ds in self.datasources]

    def get_metric_count_async(self) -> int:
        """Get total number of metrics being collected"""
        total = 0
        for metric_data in self._latest_metrics.values():
            total += len(metric_data.metrics)
        return total

    async def update_thresholds_async(self, thresholds_config: List[Dict]):
        """Update thresholds dynamically"""
        try:
            new_thresholds = []
            for config in thresholds_config:
                threshold = Threshold(
                    metric_name=config['metric'],
                    operator=config['operator'],
                    value=config['value'],
                    severity=Severity(config.get('severity', Severity.WARNING)),
                    message=config.get('message'),
                    datasource_filter=config.get('datasource_filter')
                )
                new_thresholds.append(threshold)

            self.thresholds = new_thresholds
            logger.info(f"Updated {len(new_thresholds)} thresholds")

        except Exception as e:
            raise ThresholdException(f"Failed to update thresholds: {e}")

    async def add_datasource_async(self, datasource_config: Dict):
        """Add data source dynamically"""
        # This would use a factory pattern to create the appropriate datasource
        # based on the config type
        raise NotImplementedError("Dynamic datasource addition not implemented")

    async def remove_datasource_async(self, datasource_name: str):
        """Remove data source dynamically"""
        datasource = next((ds for ds in self.datasources if ds.name == datasource_name), None)
        if datasource:
            await datasource.close()
            self.remove_datasource(datasource_name)
        else:
            raise DataSourceException(f"Data source '{datasource_name}' not found")

    async def stream_alerts_async(self):
        """Async generator for streaming alerts"""
        last_violation_count = len(self._violation_history)

        while self._running:
            current_violation_count = len(self._violation_history)

            if current_violation_count > last_violation_count:
                # New violations occurred
                new_violations = self._violation_history[last_violation_count:]
                for violation in new_violations:
                    yield violation

                last_violation_count = current_violation_count

            await asyncio.sleep(1)

    async def stream_metrics_async(self):
        """Async generator for streaming metrics"""
        last_metrics = {}

        while self._running:
            current_metrics = await self.get_latest_metrics_async()

            # Check for new or updated metrics
            for source_name, metrics in current_metrics.items():
                if (source_name not in last_metrics or
                        metrics['timestamp'] != last_metrics.get(source_name, {}).get('timestamp')):
                    yield {source_name: metrics}

            last_metrics = current_metrics
            await asyncio.sleep(5)  # Stream every 5 seconds
