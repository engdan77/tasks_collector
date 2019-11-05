import os
from pathlib import Path
from tasks_collector.tasksdb.api import get_default_db_path


def test_get_default_db_path(monkeypatch, tmp_path):
    monkeypatch.setattr('os.path.abspath', lambda x: tmp_path)
    monkeypatch.setattr('tasks_collector.tasksdb.api.user_config_dir', lambda x: tmp_path)
    assert Path(get_default_db_path()).parent.is_dir()
