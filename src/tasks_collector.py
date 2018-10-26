#!/usr/bin/env python

"""project_name: Small project for collecting tickets"""
import argparse
from jira import JIRA
import re
import datetime as dt
from reportgenerator import tasks_to_pastebin
from tasksscraper.outlookscraper import get_outlook_tasks
from tasksconverter import to_generic
from reportgenerator import filter_generic_tasks
from tasksdb import OpenDB

# import keyring

__author__ = "Daniel Engvall"
__email__ = "daniel@engvalls.eu"


def get_all_ticket(jira_password):
    # options = {'server': 'https://cog-jira.ipsoft.com', 'basic_auth': ('dengvall', pwd)}
    jira = JIRA(basic_auth=('dengvall', jira_password), server='https://cog-jira.ipsoft.com')

    # Get all projects viewable by anonymous users.
    projects = jira.projects()
    project = jira.project(10106)
    issues_in_proj = jira.search_issues('project=SEB')
    oh_crap = jira.search_issues('assignee = currentUser() order by priority desc', maxResults=5)
    a = oh_crap[0].__dict__['key']
    b = [oh_crap[0].fields.summary,
         oh_crap[0].fields.created,
         oh_crap[0].fields.description,
         oh_crap[0].fields.labels,
         oh_crap[0].fields.resolutiondate,
         oh_crap[0].fields.status.name]

    # Sort available project keys, then return the second, third, and fourth keys.
    keys = sorted([project.key for project in projects])

    # Get an issue.
    issue = jira.issue('SEB-478')

    # Find all comments made by Atlassians on this issue.
    atl_comments = [comment for comment in issue.fields.comment.comments
                    if re.search(r'@atlassian.com$', comment.author.emailAddress)]

    pass


# noinspection PyPep8
if __name__ == '__main__':
    # pwd = keyring.get_password("tasks_collector", "daniel.engvall@ipsoft.com")
    # get_all_ticket(pwd)

    argparser = argparse.ArgumentParser(
        description='A program for parsing any selected tasks items in Outlook and generate report to pastebin')
    argparser.add_argument('--outlook', action='store_true')
    argparser.add_argument('--jirs', action='store_true')
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


    filtered_tasks = filter_generic_tasks(generic_tasks, from_date=_from, to_date=_to)

    if args.sqlite_export:
        db = OpenDB(args.sqlite_export)
        db.insert_tasks(filtered_tasks)
    tasks_to_pastebin(filtered_tasks, _filter=True, show_gantt=False)
