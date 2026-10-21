import sqlite3
from datetime import datetime

DEFAULT_DB_PATH = "alerts.db"


class AlertDB:
    def __init__(self, db_path=DEFAULT_DB_PATH):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._create_table()

    def _create_table(self):
        with self.conn:
            self.conn.execute(
                """
                CREATE TABLE IF NOT EXISTS alert_runtime (
                    alert_name TEXT PRIMARY KEY,
                    last_run TIMESTAMP
                )
            """
            )

    def get_last_run(self, alert_name):
        cur = self.conn.cursor()
        cur.execute(
            "SELECT last_run FROM alert_runtime WHERE alert_name=?", (alert_name,)
        )
        row = cur.fetchone()
        return datetime.fromisoformat(row[0]) if row else None

    def update_last_run(self, alert_name, run_time):
        with self.conn:
            self.conn.execute(
                """
                INSERT INTO alert_runtime (alert_name, last_run)
                VALUES (?, ?)
                ON CONFLICT(alert_name) DO UPDATE SET last_run=excluded.last_run
            """,
                (alert_name, run_time.isoformat()),
            )

    def close(self):
        self.conn.close()
