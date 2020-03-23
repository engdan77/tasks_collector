#!/usr/bin/env python

"""project_name: Small project for collecting tickets"""
from gooey import Gooey, GooeyParser
import argparse
import datetime as dt
import keyring
from getpass import getpass
import sys
from loguru import logger

from tasks_collector import reportgenerator
from tasks_collector.reportgenerator.api import filter_generic_tasks, tasks_to_pastebin, create_gantt_list
from tasks_collector.tasksconverter.api import to_generic
from tasks_collector.tasksdb.api import get_default_db_path, insert_or_updates_tasks, OpenDB, cleanup
from tasks_collector.tasksscraper.jirascraper import get_jira_tasks
from tasks_collector.tasksscraper.trelloscraper import get_trello_tasks
import tasks_collector.tasksscraper.outlookscraper

__author__ = "Daniel Engvall"
__email__ = "daniel@engvalls.eu"
__version__ = "0.9.5"


def get_keyring(system, username):
    password = keyring.get_password(system, username)
    if not password:
        password = getpass()
        keyring.set_password(system, username, password)
    return password


def get_args():
    default_db_path = get_default_db_path()
    app_description = 'A program for parsing any selected tasks\nitems in Outlook and/or Jira and generate report to pastebin'
    db_args = ('--sqlite_database',)
    db_kwargs = dict(help='name of sqlite to export/update to',
                     default=default_db_path)
    if not gui_disabled:
        db_kwargs['widget'] = 'FileChooser'
        argparser = GooeyParser(description=app_description)
    else:
        argparser = argparse.ArgumentParser(description=app_description)

    argparser.add_argument('--loglevel', default='INFO', choices=['INFO', 'DEBUG'])
    argparser.set_defaults(which='none')
    subparsers = argparser.add_subparsers(help='commands')
    collect_parser = subparsers.add_parser('collect')
    collect_parser.add_argument('--outlook', action='store_true')
    collect_parser.add_argument('--jira', help='username@jiraserver')
    collect_parser.add_argument('--trello', help='api_key:token:token_secret:my_name')
    # collect_parser.add_argument('--sqlite_database', help='name of sqlite to export/update to', default=default_db_path, widget='FileChooser')
    collect_parser.add_argument(*db_args, **db_kwargs)
    collect_parser.add_argument('--loglevel', default='INFO', choices=['INFO', 'DEBUG'])
    collect_parser.set_defaults(which='collect')
    report_parser = subparsers.add_parser('report')
    report_parser.add_argument('--days', type=int, default=10, metavar='number_of_days_in_past',
                           help='Number of days to cover in the report')
    report_parser.add_argument(*db_args, **db_kwargs)
    report_parser.add_argument('--copyq', action='store_true', help='paste output as MIME to pastebin, good for sending by e-mail')
    report_parser.add_argument('--show', action='store_true', help='show gantt image')
    report_parser.add_argument('--default_client', type=str, default='MyCompany', metavar='name of default client')
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
    global gui_disabled
    gui_disabled = '--ignore-gooey' in sys.argv
    if gui_disabled:
        logger.info('no gui')
        sys.argv.remove('--ignore-gooey')
        args, default_db_path = get_args()
    else:
        logger.info('gui')
        # TODO: some tricky things need to be fixed to able to --ignore-gooey
        return Gooey(get_args, program_name='Tasks Collector', navigation='TABBED')()

    logger.remove()
    logger.add(sys.stderr, level=args.loglevel, colorize=not gui_disabled)

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
            tasks_to_pastebin(filtered_tasks, _filter=True, show_gantt=False, default_client=args.default_client)
        if args.show:
            gantt_list = create_gantt_list(filtered_tasks, args.default_client)
            reportgenerator.api.get_gantt_b64(gantt_list, show_gantt=True)
        sys.exit(0)

    if 'before' in args.__dict__.keys():
        logger.info('cleanup initiated')
        now = dt.datetime.now()
        days = dt.timedelta(days=args.__dict__['before'])
        _before = (now - days)
        logger.info(f'cleanup before {_before}')
        cleanup(_before)
        sys.exit(0)

    # Else fetch data
    if args.which == 'collect':
        logger.info('collection initiated!')
        generic_tasks = []
        if 'outlook' in args and args.outlook:
            outlook_tasks = tasks_collector.tasksscraper.outlookscraper.get_outlook_tasks()
            if not outlook_tasks:
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

        if 'trello' in args and args.trello:
            api_key, token, token_secret, my_name = args.trello.split(':')
            trello_tasks = get_trello_tasks(api_key, token, token_secret, my_name)
            trello_generic_tasks = to_generic(trello_tasks, _type='trello')
            generic_tasks.extend(trello_generic_tasks)

        insert_or_updates_tasks(generic_tasks)


# noinspection PyPep8
if __name__ == '__main__':
    logger.remove()
    logger.add(sys.stderr, level="INFO", colorize=False)
    logger.info('Pass argument --ignore-gooey to use CLI')
    main()
