#!/usr/bin/env python

"""tasksconverter: ...."""

__author__ = "Daniel Engvall"
__email__ = "daniel@engvalls.eu"

import dateparser
from datetime import timedelta, datetime
from loguru import logger
from typing import List, Dict, Union, Optional


def format_subject(subject: str, _type='outlook') -> str:
    """Properly format subject

    Args:
        subject:
        _type:

    Returns:

    """
    import re
    # Highlight keywords
    subject = re.sub('(@\w+\([^\]]+\))', '<b>\\1</b>', subject)
    return subject


def parse_category(category_list: List, _type='outlook') -> Dict:
    """Parse categories

    Args:
        category_list:
        _type:

    Returns:

    """
    import re

    if _type == 'outlook':
        rules = {'client': '\(([^\}]+)\)',
                 'category': '\{([^\}]+)\}'}
        result = {}
        for _type in rules.keys():
            result.update({_type: None})
        for category in category_list:
            for _type in rules.keys():
                match = re.search(rules[_type], category)
                if match:
                    result.update({_type: match.group(1)})
        return result


def convert_date_attribute(date: Union[datetime, str]) -> Optional[str]:
    """Converting date attribute

    Args:
        date:

    Returns:

    """
    import datetime
    if type(date) is datetime.datetime:
        out_date = date.strftime('%Y-%m-%d')
    elif date is None:
        out_date = None
    else:
        parsed_date = dateparser.parse(str(date))
        if parsed_date:
            out_date = parsed_date.strftime('%Y-%m-%d')
        else:
            out_date = None
    return out_date


def correct_task(input_dict: Dict) -> Union[str, Dict]:
    """Correcting the task

    Args:
        input_dict:

    Returns:

    """
    i = input_dict
    logger.debug(f'correcting dates in {input_dict}')
    # make sure there is a start date
    start_date = dateparser.parse(str(i.get('start_date', None)))
    close_date = dateparser.parse(str(i.get('close_date', None)))
    if any(((not start_date and close_date), (start_date and close_date and close_date <= start_date))):
        i['start_date'] = (dateparser.parse(i['close_date']) - timedelta(days=1)).strftime('%Y-%m-%d')
    return i


# noinspection PyUnboundLocalVariable,PyUnboundLocalVariable
def to_generic(tasks_list: List, _type='outlook') -> List:
    """Make list of tasks generic

    Args:
        tasks_list:
        _type:

    Returns:
        New list of generic tasks

    """
    generic_list = list()
    for task in tasks_list:
        if _type == 'outlook':
            logger.debug('converting outlook to generic')
            subject = format_subject(task['taskName'], _type='outlook')
            categories = task['taskCategories']
            categories = parse_category(categories, _type='outlook')
            client, category = categories['client'], categories['category']
            due_date = convert_date_attribute(task['due'])
            start_date = convert_date_attribute(task['startDate'])
            modified_date = convert_date_attribute(task['modifiedDate'])
            close_date = convert_date_attribute(task['completeDate'])
            if close_date:
                status = 'close'
            else:
                status = 'open'
        elif _type == 'jira':
            logger.debug('converting jira to generic')
            key = task.key
            subject = f'[{key}] {task.fields.summary}'
            client = task.fields.project.name
            category = None
            start_date = convert_date_attribute(task.fields.created)
            close_date = convert_date_attribute(task.fields.resolutiondate)
            modified_date = convert_date_attribute(task.fields.updated)
            due_date = convert_date_attribute(task.fields.duedate)
            status = 'open' if not any([_ in task.fields.status.name for _ in ('Done', 'Not in Scope')]) else 'close'
            # fix None dates
            if not close_date and status == 'close':
                close_date = modified_date
            if not due_date:
                due_date = modified_date
        elif _type == 'trello':
            logger.debug('converting trello to generic')
            key = task['project']
            subject = f'[{key}] {task["name"]}'
            client = ''
            category = None
            status = 'open' if task['closed'] is False else 'close'
            due_date = convert_date_attribute(task['due'])
            start_date = dateparser.parse(task['dateLastActivity']) - timedelta(days=5)
            if due_date:
                start_date = (dateparser.parse(task['due']) - timedelta(days=5)).strftime('%Y-%m-%d')
            else:
                start_date = start_date.strftime('%Y-%m-%d')
            if status == 'open':
                close_date = None
            else:
                close_date = convert_date_attribute(task['dateLastActivity'])
            modified_date = convert_date_attribute(task['dateLastActivity'])


            # fix None dates
            if not close_date and status == 'close':
                close_date = modified_date
            if not due_date:
                due_date = modified_date

        generic_task = {'subject': subject,
                        'client': client,
                        'category': category,
                        'start_date': start_date,
                        'close_date': close_date,
                        'due_date': due_date,
                        'modified_date': modified_date,
                        'status': status}
        generic_task = correct_task(generic_task)
        generic_list.append(generic_task)
    # sort the list
    generic_list = sorted(generic_list, key=lambda x: (str(x['client']), str(x['category']), str(x['status'])))
    logger.debug('complete converting to generic')
    return generic_list

