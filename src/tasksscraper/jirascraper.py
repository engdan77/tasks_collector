#!/usr/bin/env python

"""tasksscraper.jira: ...."""

__author__ = "Daniel Engvall"
__email__ = "daniel@engvalls.eu"

from jira import JIRA
from logzero import logger
# import keyring


def get_jira_tasks(host, username, jira_password, max_results=1000):
    # options = {'server': 'https://cog-jira.ipsoft.com', 'basic_auth': ('dengvall', pwd)}
    jira = JIRA(basic_auth=(username, jira_password), server=f'https://{host}')

    # Get all projects
    # projects = jira.projects()

    logger.info('fetching jira tickets')
    all_tickets = jira.search_issues('assignee = currentUser() order by priority desc', maxResults=max_results)
    logger.info(f'complete fetching {len(all_tickets)} tickets')
    return all_tickets
