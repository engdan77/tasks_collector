#!/usr/bin/env python

"""tasksdb: ...."""

import peewee as pw
from logzero import logger

# Database model
class BaseModel(pw.Model):
    class Meta:
        database = db

class Task(BaseModel):
    subject = pw.CharField(unique=True)
    client = pw.CharField()
    category = pw.CharField()
    start_date = pw.DateField()
    end_date = pw.DateField()
    due_date = pw.DateField()
    modified_date = pw.DateField()
    status = pw.CharField()

class OpenDB(Objec):
    def __init__(self, db_file, type='sqlite'):
        db = pw.SqliteDatabase(db_file)
        db.connect()
        db.create_tables(['Task'])
        self.db = db
        return self.db

    def insert_tasks(self, tasks_list_dict):
        for t in tasks_list_dict:
            rowid = (User
                     .insert(subject=t['subject'], status=t['status'])
                     .on_conflict(conflict_target=[Task.subject],
                update={Task.statust: t['status']},
                preserve=[Task.subject]).execute())
            logger.debug(rowid)
