#!/usr/bin/env python

"""tasksdb: ...."""

import peewee as pw
from loguru import logger
import datetime
from dictdiffer import diff
from appdirs import user_config_dir
from pathlib import Path
import os
from typing import Dict, List

db = pw.SqliteDatabase(None)
now = datetime.datetime.now()


# Database model
class BaseModel(pw.Model):
    class Meta:
        database = db


class Task(BaseModel):
    subject = pw.CharField(unique=True)
    client = pw.CharField(null=True)
    category = pw.CharField(null=True)
    start_date = pw.DateField(null=True)
    close_date = pw.DateField(null=True)
    due_date = pw.DateField(null=True)
    modified_date = pw.DateField(null=True)
    status = pw.CharField(null=True)


def get_default_db_path() -> str:
    """Get a default database path

    Returns:
        str: path
    """
    p = globals().get('__package__')
    local_config_dir = next(iter([d / 'config' for d in list(Path(os.path.abspath(__file__)).parents)[:2] if (d / 'config').exists()]), None)
    if local_config_dir and local_config_dir.exists():
        logger.debug(f'found local config directory in {local_config_dir}')
        base_config_dir = local_config_dir
    else:
        base_config_dir = user_config_dir(p)
        logger.debug(f'no local config directory, directory will be used {base_config_dir}')
    conf_path = Path(base_config_dir) / Path(f'{p}.sqlite')
    conf_path.parent.mkdir(parents=True, exist_ok=True)
    return str(conf_path)


def get_kv_task_as_text(task: Task, remove_keys: List=['id']) -> Dict:
    t = dict([(k, v.strftime('%Y-%m-%d')) if isinstance(v, datetime.date) else (k, v) for k, v in task.items()])
    for _id in remove_keys:
        t.pop(_id)
    return t


def insert_or_updates_tasks(tasks_list_dict: List) -> None:
    """Insert or update task

    Args:
        tasks_list_dict: List of tasks to update

    Returns:
        None

    """
    for t in tasks_list_dict:
        # only works with sqlite 3.24.0
        # rowid = (Task
        #          .insert(subject=t['subject'], status=t['status'])
        #          .on_conflict(conflict_target=[Task.subject],
        #     update={Task.status: t['status']},
        #     preserve=[Task.subject]).execute())

        try:
            task, created = Task.get_or_create(subject=t['subject'], defaults=t)
            database_record = task.__dict__['__data__']
        except pw.IntegrityError as e:
            logger.warning(f'unable to create database row for {t} due to {e}')
            created = False
        else:
            if not created:
                dict_database_record = get_kv_task_as_text(database_record)
                dict_new_record = t
                if not dict_database_record == dict_new_record:
                    logger.info(f'updating record "{t["subject"]}" {list(diff(dict_database_record, dict_new_record))}')
                    Task.update(t).where(Task.subject == t['subject']).execute()
        logger.debug(f'record created: {created}')


def cleanup(before_date):
    """Cleanup the database

    Args:
        before_date:

    Returns:
        None

    """
    tasks = Task.select().where((Task.start_date <= before_date) & (Task.status == 'open'))
    logger.info('closing following tasks:')
    for t in tasks:
        logger.info(t.subject)
    tasks = Task.update(status='close').where((Task.start_date <= before_date) & (Task.status == 'open')).execute()

    logger.info('closing following closed tasks without close date closing today:')
    tasks = Task.select().where((Task.start_date <= before_date) & (Task.status == 'close') & (Task.close_date == None))
    for t in tasks:
        logger.info(t.subject)
    Task.update(close_date=datetime.datetime.now()).where((Task.start_date <= before_date) & (Task.status == 'close') & (Task.close_date == None)).execute()
    logger.info('cleanup complete')


class OpenDB(object):
    """A class to simplify creation of a database."""
    def __init__(self, db_file, _type='sqlite'):
        db.init(db_file)
        db.connect()
        db.create_tables([Task], safe=True)
        self.db = db

    @staticmethod
    def get_all_tasks() -> List:
        all_tasks = []
        for task in Task.select():
            t = task.__dict__['__data__']
            t.pop('id')
            all_tasks.append(t)
        return all_tasks
