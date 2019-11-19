from datetime import date as d
from pathlib import Path
from tasks_collector.tasksdb.api import get_default_db_path, insert_or_updates_tasks
from tasks_collector.tasksdb.api import OpenDB, cleanup
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


@pytest.fixture
def sample_task():
    t = {'subject': '[xxx-656] Helping xxx with escalations after xxx-Dev upgrade to 3.5',
         'client': 'xxx',
         'category': None,
         'start_date': '2018-11-14',
         'close_date': '2018-11-15',
         'due_date': '2018-11-15',
         'modified_date': '2018-11-15',
         'status': 'close'}
    return t


@pytest.fixture
def setup_initial_task(setup_db, mocker, sample_task):
    db, Task = setup_db
    db = OpenDB(':memory:')
    Task.get_or_create(subject='Foo Bar', defaults=sample_task)
    mocker.patch('tasks_collector.tasksdb.api.Task', Task)
    return db, Task


def test_insert_or_updates_tasks(setup_initial_task, sample_task):
    t2 = sample_task.copy()
    t2['subject'] = 'Foo Bar'
    task_list = [sample_task, t2]
    db, Task = setup_initial_task
    insert_or_updates_tasks(task_list)
    assert len(list(Task.select())) == 2


def test_get_all_tasks(setup_initial_task):
    db, Task = setup_initial_task
    all_tasks = db.get_all_tasks()
    assert 'xxx' in all_tasks[0]['subject']


def test_cleanup(setup_initial_task, sample_task):
    db, Task = setup_initial_task
    t2 = sample_task.copy()
    t2['subject'] = 'Foo Bar'
    t2['start_date'] = '2019-01-10'
    t2['close_date'] = None
    insert_or_updates_tasks([t2])
    cleanup('2019-01-20')
    assert Task.select().order_by(Task.id.desc()).get().close_date == d.today()
