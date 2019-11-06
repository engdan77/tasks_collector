import pytest
from tasks_collector.tasksconverter.api import to_generic
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


@pytest.mark.parametrize('input_file,input_type,output_dotted,expected_len', [('jira_tasks.json', 'jira', True, 2)])
def test_to_generic(input_file, input_type, output_dotted, expected_len, caplog):
    with open(input_file) as f:
        input_list = json.loads(f.read())
    if output_dotted:
        l = []
        for _ in input_list:
            l.append(AttrDict(_))
        input_list = l
    generic_list = to_generic(input_list, _type=input_type)
    print(len(caplog.records))
    assert len(generic_list) == expected_len
