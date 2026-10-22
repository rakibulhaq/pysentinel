from datetime import datetime

from pysentinel.utils.alert_db import AlertDB


def test_get_last_run_returns_none_for_unknown_alert(tmp_path):
    db = AlertDB(str(tmp_path / "alerts.db"))
    assert db.get_last_run("missing") is None
    db.close()


def test_update_last_run_round_trips(tmp_path):
    db = AlertDB(str(tmp_path / "alerts.db"))
    run_time = datetime(2026, 1, 1, 12, 0, 0)
    db.update_last_run("cpu", run_time)
    assert db.get_last_run("cpu") == run_time
    db.close()


def test_update_last_run_overwrites_previous_value(tmp_path):
    db = AlertDB(str(tmp_path / "alerts.db"))
    db.update_last_run("cpu", datetime(2026, 1, 1, 12, 0, 0))
    db.update_last_run("cpu", datetime(2026, 1, 1, 13, 0, 0))
    assert db.get_last_run("cpu") == datetime(2026, 1, 1, 13, 0, 0)
    db.close()


def test_last_run_persists_across_connections(tmp_path):
    path = str(tmp_path / "alerts.db")
    db = AlertDB(path)
    db.update_last_run("cpu", datetime(2026, 1, 1, 12, 0, 0))
    db.close()

    reopened = AlertDB(path)
    assert reopened.get_last_run("cpu") == datetime(2026, 1, 1, 12, 0, 0)
    reopened.close()
