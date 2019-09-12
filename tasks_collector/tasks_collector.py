#!/usr/bin/env python

"""project_name: Small project for collecting tickets"""
from gooey import Gooey
import argparse
import datetime as dt
import keyring
from getpass import getpass
import sys
import logzero
from logzero import logger
import logging
import applescript

from tasks_collector import reportgenerator
from tasks_collector.reportgenerator.api import filter_generic_tasks, tasks_to_pastebin, create_gantt_list
from tasks_collector.tasksconverter.api import to_generic
from tasks_collector.tasksdb.api import get_default_db_path, OpenDB
from tasks_collector.tasksscraper.jirascraper import get_jira_tasks
import tasks_collector.tasksscraper.outlookscraper

__author__ = "Daniel Engvall"
__email__ = "daniel@engvalls.eu"
__version__ = "0.9.0"


def get_keyring(system, username):
    password = keyring.get_password(system, username)
    if not password:
        password = getpass()
        keyring.set_password(system, username, password)
    return password


@Gooey
def get_args():
    default_db_path = get_default_db_path()
    argparser = argparse.ArgumentParser(
        description='A program for parsing any selected tasks items in Outlook and/or Jira and generate report to pastebin')
    argparser.add_argument('--loglevel', default='INFO', choices=['INFO', 'DEBUG'])
    subparsers = argparser.add_subparsers(help='commands')
    collect_parser = subparsers.add_parser('collect')
    collect_parser.add_argument('--outlook', action='store_true')
    collect_parser.add_argument('--jira', help='username@jiraserver')
    collect_parser.add_argument('--sqlite_database', default=default_db_path, help='name of sqlite to export/update to')
    collect_parser.add_argument('--loglevel', default='INFO', choices=['INFO', 'DEBUG'])
    collect_parser.set_defaults(which='collect')
    report_parser = subparsers.add_parser('report')
    report_parser.add_argument('--days', type=int, default=10, metavar='number_of_days_in_past',
                           help='Number of days to cover in the report')
    report_parser.add_argument('--sqlite_database', default=default_db_path, help='name of sqlite to get data from')
    report_parser.add_argument('--copyq', action='store_true', help='paste output as MIME to pastebin, good for sending by e-mail')
    report_parser.add_argument('--show', action='store_true', help='show gantt image')
    report_parser.add_argument('--loglevel', default='INFO', choices=['INFO', 'DEBUG'])
    report_parser.set_defaults(which='report')
    cleanup_parser = subparsers.add_parser('cleanup')
    cleanup_parser.add_argument('--before', type=int, metavar='DAYS', help='tickets before this number of days back to be closed')
    cleanup_parser.add_argument('--sqlite_database', default=default_db_path, help='name of sqlite to export/update to')
    cleanup_parser.add_argument('--loglevel', default='INFO', choices=['INFO', 'DEBUG'])
    cleanup_parser.set_defaults(which='cleanup')
    args = argparser.parse_args()
    return args, default_db_path



def main():
    args, default_db_path = get_args()
    logzero.loglevel(getattr(logging, args.loglevel))
    if 'sqlite_database' not in args.__dict__.keys():
        db_path = default_db_path
    else:
        db_path = args.sqlite_database
    db = OpenDB(db_path)

    if 'days' in args.__dict__.keys():
        logger.info('report command initiated')
        now = dt.datetime.now()
        days = dt.timedelta(days=args.days)
        _from = (now - days).strftime('%Y-%m-%d')
        _to = (now + days).strftime('%Y-%m-%d')
        all_tasks = db.get_all_tasks()
        filtered_tasks = filter_generic_tasks(all_tasks, from_date=_from, to_date=_to)
        if args.copyq:
            tasks_to_pastebin(filtered_tasks, _filter=True, show_gantt=False)
        if args.show:
            gantt_list = create_gantt_list(filtered_tasks)
            reportgenerator.api.get_gantt_b64(gantt_list, show_gantt=True)
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
    if args.which == 'collect':
        logger.info('collection initiated')
        generic_tasks = []
        if 'outlook' in args and args.outlook:
            try:
                outlook_tasks = tasks_collector.tasksscraper.outlookscraper.get_outlook_tasks()
            except applescript.ScriptError:
                logger.warning('Unable to retrieve outlook tasks, make sure Outlook has been started')
            else:
                outlook_generic_tasks = to_generic(outlook_tasks, _type='outlook')
                generic_tasks.extend(outlook_generic_tasks)

        if 'jira' in args and args.jira:
            username, host = args.jira.split('@', 1)
            password = get_keyring('tasks_collector', username)
            jira_tasks = get_jira_tasks(host, username, password)
            jira_generic_tasks = to_generic(jira_tasks, _type='jira')
            generic_tasks.extend(jira_generic_tasks)
        db.insert_or_updates_tasks(generic_tasks)


# noinspection PyPep8
if __name__ == '__main__':
    if '--ignore-gooey' in sys.argv:
        logger.info('Disabling GUI')
    main()
