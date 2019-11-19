from tasks_collector.tasksscraper.outlookscraper import get_outlook_tasks
import json

def test_get_outlook_tasks(mocker):
    with open('outlook_tasks.json') as f:
        input_list = json.loads(f.read())
    mocked_outlook = mocker.patch('tasks_collector.tasksscraper.outlookscraper.applescript.AppleScript')
    mocked_outlook.return_value.call.return_value = input_list
    all_tasks = get_outlook_tasks()
    assert mocked_outlook.call_count == 1
    assert len(all_tasks) == 2
