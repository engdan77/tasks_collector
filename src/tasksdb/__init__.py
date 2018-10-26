#!/usr/bin/env python

"""tasksdb: ...."""

import peewee as pw
from logzero import logger
import datetime

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
    start_date = pw.DateField(default=now)
    close_date = pw.DateField(default=now)
    due_date = pw.DateField(default=now)
    modified_date = pw.DateField(default=now)
    status = pw.CharField(null=True)

class OpenDB(object):
    def __init__(self, db_file, type='sqlite'):
        db.init(db_file)
        db.connect()
        db.create_tables([Task], safe=True)
        self.db = db

    def insert_tasks(self, tasks_list_dict):
        for t in tasks_list_dict:
            # only works with sqlite 3.24.0
            # rowid = (Task
            #          .insert(subject=t['subject'], status=t['status'])
            #          .on_conflict(conflict_target=[Task.subject],
            #     update={Task.status: t['status']},
            #     preserve=[Task.subject]).execute())

            try:
                task, created = Task.get_or_create(subject = t['subject'], defaults=t)
            except pw.IntegrityError as e:
                logger.warning(f'unable to create database row for {t} due to {e}')
                created = False
            logger.debug(f'record created: {created}')
