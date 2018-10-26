#!/usr/bin/env python

"""tasksconverter: ...."""

__author__ = "Daniel Engvall"
__email__ = "daniel@engvalls.eu"

import dateparser

def format_subject(subject, _type='outlook'):
    import re
    # Highlight keywords
    subject = re.sub('(@\w+\([^\]]+\))', '<b>\\1</b>', subject)
    return subject

def parse_category(category_list, _type='outlook'):
    """
    Returns a dict with type of items
    :param _type:
    :param category_list:
    :return:
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
                match = re.match(rules[_type], category)
                if match:
                    result.update({_type: match.group(1)})
        return result

def convert_date_attribute(date):
    import datetime
    if type(date) is datetime.datetime:
        out_date = date.strftime('%Y-%m-%d')
    elif date is None:
        out_date = None
    else:
        parsed_date = dateparser.parse(date)
        if parsed_date:
            out_date = parsed_date.strftime('%Y-%m-%d')
        else:
            out_date = None
    return out_date


# noinspection PyUnboundLocalVariable,PyUnboundLocalVariable
def to_generic(tasks_list, _type='outlook'):
    generic_list = list()
    for task in tasks_list:
        if _type == 'outlook':
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
            key = task.key
            subject = f'[{key}] {task.fields.summary}'
            client = task.fields.project.name
            category = None
            start_date = convert_date_attribute(task.fields.created)
            close_date = convert_date_attribute(task.fields.resolutiondate)
            modified_date = convert_date_attribute(task.fields.updated)
            due_date = convert_date_attribute(task.fields.duedate)
            status = 'open' if not task.fields.status.name == 'Done' else 'close'
            # fix None dates
            if not close_date:
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
        generic_list.append(generic_task)
    # sort the list
    generic_list = sorted(generic_list, key=lambda x: (str(x['client']), str(x['category']), str(x['status'])))
    return generic_list



