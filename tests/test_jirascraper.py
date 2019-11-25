from tasks_collector.tasksscraper.jirascraper import get_jira_tasks
import json

def test_get_jira_tasks(mocker):
    with open('tests/jira_tasks.json') as f:
        input_list = json.loads(f.read())
    mocked_jira = mocker.patch('tasks_collector.tasksscraper.jirascraper.JIRA')
    mocked_jira.return_value.search_issues.return_value = input_list
    all_tasks = get_jira_tasks('server', 'username', 'password')
    assert mocked_jira.call_count == 1
    assert len(all_tasks) == 2
