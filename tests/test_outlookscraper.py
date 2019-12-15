from tasks_collector.tasksscraper.outlookscraper import get_outlook_tasks, remove_invalid_brackets, fix_quotes_json_strings
import json


def test_get_outlook_tasks(mocker):
    with open('tests/outlook_tasks.json') as f:
        input_list = json.loads(f.read())
    input_list = (0, '{"taskName": "Third task",'
                     '"taskContent": "","taskFolder": '
                     '"Tasks","modifiedDate": '
                     '"Sunday, 24 November 2019 at 20:09:04",'
                     '"startDate": "Saturday, 23 November 2019 at 00:00:00",'
                     '"due": "Friday, 29 November 2019 at 00:00:00",'
                     '"completeDate": "missing value",'
                     '"taskPriority": "priority normal",'
                     '"taskCategories": ["{Project X}","(Client 1)"]},'
                     '{"taskName": "The second task",'
                     '"taskContent": "",'
                     '"taskFolder": "Tasks",'
                     '"modifiedDate": "Sunday, 24 November 2019 at 22:39:00",'
                     '"startDate": "Monday, 16 September 2019 at 00:00:00",'
                     '"due": "Thursday, 19 September 2019 at 00:00:00",'
                     '"completeDate": "Sunday, 24 November 2019 at 22:39:00",'
                     '"taskPriority": "priority normal",'
                     '"taskCategories": ["{Project Y}","(Client 1)"]},'
                     '{"taskName": "My first task",'
                     '"taskContent": "","taskFolder": '
                     '"Tasks","modifiedDate": "Sunday, 24 November 2019 at 20:09:36",'
                     '"startDate": "Tuesday, 3 September 2019 at 00:00:00",'
                     '"due": "Wednesday, 11 September 2019 at 00:00:00",'
                     '"completeDate": "missing value",'
                     '"taskPriority": "priority normal",'
                     '"taskCategories": ["(Client 2)"]},', '')
    mocked_outlook = mocker.patch('tasks_collector.tasksscraper.outlookscraper.osascript')
    mocked_outlook.run.return_value = input_list
    all_tasks = get_outlook_tasks()
    assert mocked_outlook.run.call_count == 1
    assert len(all_tasks) == 3


def test_remove_invalid_brackets():
    invalid_json = '[{"foo":"bar"},{{{"bar":"foo"}]'
    assert remove_invalid_brackets(invalid_json) == '[{"foo":"bar"},{"bar":"foo"}]'


def test_fix_quotes_json_strings():
    invalid_json = '[{"taskName":"invalid "quotes" here","taskPriority":"priority normal"}]'
    assert fix_quotes_json_strings(invalid_json) == """[{"taskName":"invalid 'quotes' here","taskPriority":"priority normal"}]"""
