#!/usr/bin/env python

"""tasksconverter: ...."""
import subprocess
from logzero import logger
import matplotlib
# workaround for MacOS
matplotlib.use('TkAgg')

import matplotlib.pyplot as plt
import matplotlib.font_manager as font_manager
import matplotlib.legend
# noinspection PyProtectedMember
from matplotlib.dates import WEEKLY, DateFormatter, rrulewrapper, RRuleLocator
import datetime as dt
import numpy as np
import base64
import json

__author__ = "Daniel Engvall"
__email__ = "daniel@engvalls.eu"


default_client = 'IPsoft'

html_header = u'''<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
<meta http-equiv="Content-Style-Type" content="text/css">
<title></title>
<meta name="Generator" content="Cocoa HTML Writer">
<meta name="CocoaVersion" content="1404.47">
<style type="text/css">
p.p1 {margin: 0.0px 0.0px 0.0px 0.0px; font: 14.0px Helvetica; -webkit-text-stroke: #000000}
p.p2 {margin: 0.0px 0.0px 0.0px 0.0px; font: 14.0px Helvetica; color: #017f00; -webkit-text-stroke: #017f00}
span.s1 {text-decoration: underline ; font-kerning: none}
span.s2 {font-kerning: none}
</style>
</head>
<body>
'''
html_footer = '''</body>
</html>'''


def _create_date(datetxt):
    """
    Create matplot date
    :param datetxt:
    :return:
    """
    year, month, day = datetxt.split('-')
    date = dt.datetime(int(year), int(month), int(day))
    mdate = matplotlib.dates.date2num(date)
    return mdate


# noinspection PyUnboundLocalVariable
def render_task(client, category, subject, **kwargs):
    """
    Render HTML for task
    :param client:
    :param category:
    :param subject:
    :param kwargs:
    :return: task in html
    """
    status = kwargs.get('status', 'open')
    close_date = kwargs.get('close_date', None)
    due_date = kwargs.get('due_date', None)
    start_date = kwargs.get('start_date', None)
    suffix = '</span></p>'

    if status == u'open':
        prefix = u'<p class="p1"><span class="s2">     '
        char = u'☐'
    elif status == u'close':
        prefix = u'<p class="p2"><span class="s2">     '
        char = u'✔'

    # Add prefix and complete/not-complete character
    task = u'{}{}'.format(prefix, char)
    # Replace client with default if needed
    if not client:
        client = default_client
    task += u' <b>{}</b>: '.format(client)
    # Remove category if none
    if category:
        task += u'<i>{}:</i> '.format(category)
    # Add subject
    task += u'{}'.format(subject)
    # Add @start
    if start_date:
        task += u' <b>@start({})</b>'.format(start_date)
    # Add @due if needed
    if due_date:
        task += u' <b>@due({})</b>'.format(due_date)
    # Add @done
    if close_date:
        task += u' <b>@done({})</b>'.format(close_date)
    # Add suffix
    task += suffix
    return task


def create_gantt_chart(task_list, *, show_gantt=True, gantt_file='/tmp/gantt.png', dpi=72):
    """
    Creates gantt chart
    :param dpi:
    :param show_gantt:
    :param task_list:
    :param gantt_file:
    :return: return base64 encoded image
    """

    ylabels = []
    statuses = []
    custom_dates = []

    for t in task_list:
        ylabel, startdate, enddate, status = t
        statuses.append(status)
        ylabels.append(ylabel.replace('\n', ''))
        if enddate is None:
            enddate = dt.datetime.now() + dt.timedelta(days=7)
            enddate = enddate.strftime('%Y-%m-%d')
        custom_dates.append([_create_date(startdate.replace('\n', '')), _create_date(enddate.replace('\n', ''))])

    ilen = len(ylabels)
    pos = np.arange(0.5, ilen * 0.5 + 0.5, 0.5)
    task_dates = {}
    for i, task in enumerate(ylabels):
        task_dates[task] = custom_dates[i]
    fig = plt.figure(figsize=(20, 8))
    ax = fig.add_subplot(111)
    unique_legend_list = list()
    for i in range(len(ylabels)):
        start_date, end_date = task_dates[ylabels[i]]
        # Change color depending on status
        if statuses[i] == 'open':
            bar_color = 'orange'
        elif statuses[i] == 'pending':
            bar_color = 'gray'
        elif statuses[i] == 'over_due':
            bar_color = 'red'
        else:
            bar_color = 'green'
        label = statuses[i] if not statuses[i] in unique_legend_list else ""
        unique_legend_list.append(statuses[i])
        unique_legend_list = list(set(unique_legend_list))
        ax.barh((i * 0.5) + 0.5, end_date - start_date, left=start_date, height=0.3, align='center',
                edgecolor='lightgreen', color=bar_color, alpha=0.8, label=label)
    locsy, labelsy = plt.yticks(pos, ylabels)
    plt.setp(labelsy, fontsize=10)
    ax.set_ylim(ymin=-0.1, ymax=ilen * 0.5 + 0.5)
    ax.grid(color='g', linestyle=':')
    ax.xaxis_date()
    rule = rrulewrapper(WEEKLY, interval=1)
    loc = RRuleLocator(rule)
    formatter = DateFormatter("%d-%b")
    ax.xaxis.set_major_locator(loc)
    ax.xaxis.set_major_formatter(formatter)

    # Add legend
    ax.legend(loc='upper left')

    # Add red line current date
    conv = np.vectorize(matplotlib.dates.strpdate2num('%Y-%m-%d'))
    now = dt.datetime.now().strftime('%Y-%m-%d')
    # ax.axvline(conv(now), color='r', zorder=0)
    ax.axvline(float(conv(now)), color='r', zorder=0)

    labelsx = ax.get_xticklabels()
    plt.setp(labelsx, rotation=30, fontsize=10)

    font = font_manager.FontProperties(size='small')
    ax.legend(loc=1, prop=font)

    ax.invert_yaxis()
    fig.autofmt_xdate()
    plt.savefig(gantt_file, dpi=dpi, bbox_inches='tight')
    if show_gantt:
        plt.show()
    with open(gantt_file, 'rb') as f:
        gantt_b64 = base64.b64encode(f.read()).decode('utf-8')
    return gantt_b64


def tasks_to_pastebin(generic_tasks, _filter=False, show_gantt=True):
    """
    Creates tasks and inserted to pastebin
    :return:
    """
    # from_date = kwargs.get('from_date', None)
    # to_date = kwargs.get('to_date', None)
    # include_open = kwargs.get('include_open', True)

    logger.debug(json.dumps(generic_tasks))

    email_html = html_header

    gantt_list = list()

    for t in generic_tasks:
        # Render HTML for tasks
        email_html += render_task(t['client'],
                                  t['category'],
                                  t['subject'],
                                  status=t['status'],
                                  close_date=t['close_date'],
                                  due_date=t['due_date'],
                                  start_date=t['start_date'])
        # Create data for gantt
        client = default_client if not t['client'] else t['client']
        gantt_task_name = '{}:{}:{}'.format(client, t['category'], t['subject'][:30]) if t[
            'category'] else '{}:{}...'.format(client, t['subject'][:30])
        if not gantt_task_name:
            gantt_task_name = default_client
        gantt_status = t['status'] if not all(
            [not t['start_date'], not t['close_date'], not t['due_date']]) else 'pending'
        gantt_start_date = t['start_date'] if t['start_date'] else t['modified_date']
        gantt_end_date = t['close_date'] if t['close_date'] else t['due_date']
        if gantt_end_date:
            if gantt_end_date == gantt_start_date:
                gantt_end_date = (dt.datetime.strptime(gantt_end_date, '%Y-%m-%d') + dt.timedelta(days=1)).strftime(
                    '%Y-%m-%d')
            if not t['due_date'] is None:
                if dt.datetime.strptime(t['due_date'], '%Y-%m-%d') < dt.datetime.now() and not gantt_status == 'close':
                    gantt_status = 'over_due'
        gantt_list.append([gantt_task_name, gantt_start_date, gantt_end_date, gantt_status])

    # Render gantt
    gantt_b64 = create_gantt_chart(gantt_list, show_gantt=show_gantt)

    # Attach image
    email_html += '<img src="data:image/png;base64,{}" alt="gantt.png">'.format(gantt_b64)

    # Add footer
    email_html += html_footer

    logger.debug(email_html)

    proc = subprocess.Popen(['/usr/local/bin/copyq', 'copy', 'text/html', '-'],
                            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = proc.communicate(input=email_html.encode('utf-8'))
    logger.debug(out, err)


# noinspection PyPep8
def filter_generic_tasks(generic_task_list, *, from_date=None, to_date=None, include_open=True):
    import datetime
    result = []
    for t in generic_task_list:
        include_ticket = False
        if include_open and t['status'] == 'open':
            include_ticket = True
        elif all([from_date, to_date]):
            # noinspection PyPep8
            if datetime.datetime.strptime(from_date, '%Y-%m-%d') <= datetime.datetime.strptime(t['modified_date'],
                                                                                               '%Y-%m-%d') <= datetime.datetime.strptime(
                    to_date, '%Y-%m-%d'):
                include_ticket = True
        if include_ticket:
            result.append(t)
    return result
