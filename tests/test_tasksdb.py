import os
from pathlib import Path
from tasks_collector.tasksdb.api import get_default_db_path, insert_or_updates_tasks
import peewee as pw
import pytest


def test_get_default_db_path(monkeypatch, tmp_path):
    monkeypatch.setattr('os.path.abspath', lambda x: tmp_path)
    monkeypatch.setattr('tasks_collector.tasksdb.api.user_config_dir', lambda x: tmp_path)
    assert Path(get_default_db_path()).parent.is_dir()


@pytest.fixture
def setup_db():
    db = pw.SqliteDatabase(':memory:')
    class Base(pw.Model):
        class Meta:
            database = db
    class Task(Base):
        subject = pw.CharField(unique=True)
        client = pw.CharField(null=True)
        category = pw.CharField(null=True)
        start_date = pw.DateField(null=True)
        close_date = pw.DateField(null=True)
        due_date = pw.DateField(null=True)
        modified_date = pw.DateField(null=True)
        status = pw.CharField(null=True)
    db.connect()
    db.create_tables([Task], safe=True)
    return db, Task


def test_insert_or_updates_tasks(setup_db, mocker):
    t1 = {'subject': '[xxx-656] Helping xxx with escalations after xxx-Dev upgrade to 3.5',
          'client': 'xxx',
          'category': None,
          'start_date': '2018-11-14',
          'close_date': '2018-11-15',
          'due_date': '2018-11-15',
          'modified_date': '2018-11-15',
          'status': 'close'}
    t2 = t1.copy()
    t2['subject'] = 'Foo Bar'
    task_list = [t1, t2]
    db, Task = setup_db
    mocker.patch('tasks_collector.tasksdb.api.Task', Task)
    insert_or_updates_tasks(task_list)
    assert len(list(Task.select())) == 2
