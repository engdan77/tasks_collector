#!/usr/bin/env python

"""project_name: Small project for collecting tickets"""
import argparse
import datetime as dt
from reportgenerator import tasks_to_pastebin
from tasksscraper.outlookscraper import get_outlook_tasks
from tasksscraper.jirascraper import get_jira_tasks
from tasksconverter import to_generic
from reportgenerator import filter_generic_tasks
from tasksdb import OpenDB
import keyring
from getpass import getpass


# import keyring

__author__ = "Daniel Engvall"
__email__ = "daniel@engvalls.eu"


def get_keyring(system, username):
    password = keyring.get_password(system, username)
    if not password:
        password = getpass()
        keyring.set_password(system, username, password)
    return password

# noinspection PyPep8
if __name__ == '__main__':
    # pwd = keyring.get_password("tasks_collector", "daniel.engvall@ipsoft.com")
    # get_jira_tasks(pwd)

    argparser = argparse.ArgumentParser(
        description='A program for parsing any selected tasks items in Outlook and generate report to pastebin')
    argparser.add_argument('--outlook', action='store_true')
    argparser.add_argument('--jira', help='username@jiraserver')
    argparser.add_argument('--days', type=int, metavar='number_of_days_in_past',
                           help='Number of days to cover in the report')
    argparser.add_argument('--sqlite_export', type=str, help='name of sqlite to export/update to')
    args = argparser.parse_args()

    now = dt.datetime.now()

    if not args.days:
        process_days = 10
    else:
        process_days = args.days

    days = dt.timedelta(days=process_days)
    _from = (now - days).strftime('%Y-%m-%d')
    _to = (now + days).strftime('%Y-%m-%d')

    # tasks_to_pastebin(filter=True, from_date='2017-10-01', to_date='2017-12-01', sources=['outlook'], show_gantt=False)

    generic_tasks = []

    if args.outlook:
        outlook_tasks = get_outlook_tasks()
        outlook_generic_tasks = to_generic(outlook_tasks, _type='outlook')
        generic_tasks.extend(outlook_generic_tasks)

    if args.jira:
        username, host = args.jira.split('@', 1)
        password = get_keyring('tasks_collector', username)
        jira_tasks = get_jira_tasks(host, username, password)
        jira_generic_tasks = to_generic(jira_tasks, _type='jira')
        generic_tasks.extend(jira_generic_tasks)


    filtered_tasks = filter_generic_tasks(generic_tasks, from_date=_from, to_date=_to)

    if args.sqlite_export:
        db = OpenDB(args.sqlite_export)
        db.insert_tasks(filtered_tasks)
    tasks_to_pastebin(filtered_tasks, _filter=True, show_gantt=False)
