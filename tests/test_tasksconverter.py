import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)

import pytest
from tasks_collector.tasksconverter.api import to_generic, correct_task
import json
from attrdict import AttrDict
import logging
from loguru import logger


@pytest.fixture
def caplog(caplog):
    class PropogateHandler(logging.Handler):
        def emit(self, record):
            logging.getLogger(record.name).handle(record)

    logger.add(PropogateHandler(), format="{message}")
    yield caplog


@pytest.mark.parametrize('input_file,input_type,output_dotted,expected_len',
                         [('jira_tasks.json', 'jira', True, 2),
                          ('outlook_tasks.json', 'outlook', False, 2),
                          ('trello_tasks.json', 'trello', False, 2)])
def test_to_generic(input_file, input_type, output_dotted, expected_len, caplog):
    with open(input_file) as f:
        input_list = json.loads(f.read())
    if output_dotted:
        # used when the task being an object (dot notation) instead of a dict
        l = []
        for _ in input_list:
            l.append(AttrDict(_))
        input_list = l
    generic_list = to_generic(input_list, _type=input_type)
    assert len(generic_list) == expected_len, 'invalid number of records'
    assert 'complete converting to generic' in caplog.text, 'completion not found in log'


@pytest.mark.parametrize('input_dict,output_dict',
                         [({'start_date': '2018-01-20', 'close_date': '2018-01-10'},
                           {'start_date': '2018-01-09', 'close_date': '2018-01-10'}),
                          ({'close_date': '2018-01-15'},
                           {'start_date': '2018-01-14', 'close_date': '2018-01-15'}),
                          ({'start_date': '2018-02-23', 'close_date': '2018-02-27'},
                           {'start_date': '2018-02-23', 'close_date': '2018-02-27'}),
                          ])
def test_correct_task(input_dict, output_dict):
    assert correct_task(input_dict) == output_dict
