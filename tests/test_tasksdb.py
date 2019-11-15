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
def DbTask():
    db = pw.SqliteDatabase(':memory:')
    class Base(pw.Model):
        class Meta:
            database = db
    class _Task(Base):
        subject = pw.CharField(unique=True)
        client = pw.CharField(null=True)
        category = pw.CharField(null=True)
        start_date = pw.DateField(null=True)
        close_date = pw.DateField(null=True)
        due_date = pw.DateField(null=True)
        modified_date = pw.DateField(null=True)
        status = pw.CharField(null=True)
    return db, _Task


@pytest.fixture
def fix_db(DbTask):
    db, Task = DbTask
    db.connect()
    db.create_tables([Task], safe=True)
    return db, Task

def test_insert_or_updates_tasks(fix_db):
    t = {'subject': '[xxx-656] Helping xxx with escalations after xxx-Dev upgrade to 3.5',
         'client': 'xxx',
         'category': None,
         'start_date': '2018-11-14',
         'close_date': '2018-11-15',
         'due_date': '2018-11-15',
         'modified_date': '2018-11-15',
         'status': 'close'}
    task_list = [t, t.copy().update({'subject': 'foo bar'})]
    # db = pw.SqliteDatabase(':memory:')
    # db.connect()
    # db.create_tables([Task], safe=True)

    # task, created = Task.get_or_create(subject='xxxx')
    # print(list(Task.select()))
    db, Task = fix_db
    task, created = Task.get_or_create(subject='xxxx')
    print(list(Task.select()))
    insert_or_updates_tasks(task_list)
    assert 1 == 1
