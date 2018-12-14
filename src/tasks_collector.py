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
import sys
import logzero
from logzero import logger
import logging


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
    argparser = argparse.ArgumentParser(
        description='A program for parsing any selected tasks items in Outlook and/or Jira and generate report to pastebin')
    subparsers = argparser.add_subparsers(help='commands')
    collect_parser = subparsers.add_parser('collect')
    collect_parser.add_argument('--outlook', action='store_true')
    collect_parser.add_argument('--jira', help='username@jiraserver')
    collect_parser.add_argument('sqlite_database', type=str, help='name of sqlite to export/update to')
    collect_parser.add_argument('--loglevel', default='INFO', choices=['INFO', 'DEBUG'])
    report_parser = subparsers.add_parser('report')
    report_parser.add_argument('--days', type=int, default=10, metavar='number_of_days_in_past',
                           help='Number of days to cover in the report')
    report_parser.add_argument('sqlite_database', help='name of sqlite to get data from')
    report_parser.add_argument('--loglevel', default='INFO', choices=['INFO', 'DEBUG'])
    cleanup_parser = subparsers.add_parser('cleanup')
    cleanup_parser.add_argument('--before', type=int, metavar='DAYS', help='tickets before this number of days back to be closed')
    cleanup_parser.add_argument('sqlite_database', type=str, help='name of sqlite to export/update to')
    cleanup_parser.add_argument('--loglevel', default='INFO', choices=['INFO', 'DEBUG'])

    args = argparser.parse_args()
    logzero.loglevel(getattr(logging, args.loglevel))

    db = OpenDB(args.sqlite_database)

    if 'days' in args.__dict__.keys():
        logger.info('report command initiated')
        now = dt.datetime.now()
        days = dt.timedelta(days=args.days)
        _from = (now - days).strftime('%Y-%m-%d')
        _to = (now + days).strftime('%Y-%m-%d')
        all_tasks = db.get_all_tasks()
        filtered_tasks = filter_generic_tasks(all_tasks, from_date=_from, to_date=_to)
        tasks_to_pastebin(filtered_tasks, _filter=True, show_gantt=False)
        # tasks_to_pastebin(filter=True, from_date='2017-10-01', to_date='2017-12-01', sources=['outlook'], show_gantt=False)
        sys.exit(0)

    if 'before' in args.__dict__.keys():
        logger.info('cleanup initiated')
        now = dt.datetime.now()
        days = dt.timedelta(days=args.__dict__['before'])
        _before = (now - days)
        logger.info(f'cleanup before {_before}')
        db.cleanup(_before)
        sys.exit(0)


    # Else fetch data
    logger.info('collection initiated')
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

    db.insert_or_updates_tasks(generic_tasks)


