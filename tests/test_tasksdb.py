import os
from pathlib import Path
from tasks_collector.tasksdb.api import get_default_db_path
import peewee as pw


def test_get_default_db_path(monkeypatch, tmp_path):
    monkeypatch.setattr('os.path.abspath', lambda x: tmp_path)
    monkeypatch.setattr('tasks_collector.tasksdb.api.user_config_dir', lambda x: tmp_path)
    assert Path(get_default_db_path()).parent.is_dir()


@pytest.fixture(scope='session')
def db():
    return pw.SqliteDatabase(':memory:', autocommit=False)


@pytest.fixture(scope='session')
def Base(db):
    class Base(pw.Model):
        class Meta:
            database = db

    return Base


@pytest.fixture(scope='session')
def Task(Base):
    class Task(Base):
        subject = pw.CharField(unique=True)
        client = pw.CharField(null=True)
        category = pw.CharField(null=True)
        start_date = pw.DateField(null=True)
        close_date = pw.DateField(null=True)
        due_date = pw.DateField(null=True)
        modified_date = pw.DateField(null=True)
        status = pw.CharField(null=True)
    return Task


def test_insert_or_updates_tasks():
    assert False
