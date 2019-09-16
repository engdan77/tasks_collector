#!/usr/bin/env python

"""tasksscraper.jira: ...."""

__author__ = "Daniel Engvall"
__email__ = "daniel@engvalls.eu"

from jira import JIRA
from logzero import logger
from typing import List
# import keyring


def get_jira_tasks(host: str, username: str, jira_password: str, max_results: int = 1000) -> List:
    """Query Jira for tickets

    Args:
        host:
        username:
        jira_password:
        max_results:

    Returns:
        List of tasks

    """
    # options = {'server': 'https://cog-jira.ipsoft.com', 'basic_auth': ('dengvall', pwd)}
    jira = JIRA(basic_auth=(username, jira_password), server=f'https://{host}')

    # Get all projects
    # projects = jira.projects()

    logger.info('fetching jira tickets')
    all_tickets = jira.search_issues('assignee = currentUser() order by priority desc', maxResults=max_results)
    logger.info(f'complete fetching {len(all_tickets)} tickets')
    return all_tickets
