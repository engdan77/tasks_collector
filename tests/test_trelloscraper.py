from tasks_collector.tasksscraper.trelloscraper import add_project, get_trello_tasks
import json


def test_add_project():
    input_my_tasks = [{'project': 'myProject', 'idBoard': 1}]
    board_ids = {1: 'boardName'}
    assert add_project(input_my_tasks, board_ids) == [{'idBoard': 1, 'project': 'boardName'}]


def test_get_trello_tasks(mocker):
    with open('tests/trello_tasks.json') as f:
        input_list = json.loads(f.read())
    mocker.patch('tasks_collector.tasksscraper.trelloscraper.TrelloClient')
    mocker.patch('tasks_collector.tasksscraper.trelloscraper.find_my_id')
    mocker.patch('tasks_collector.tasksscraper.trelloscraper.get_all_board_ids')
    mocked_add_project = mocker.patch('tasks_collector.tasksscraper.trelloscraper.add_project')
    mocked_add_project.return_value = input_list
    trello_tasks = get_trello_tasks('api_key', 'token', 'token_secret', 'my name')
    assert len(trello_tasks) == 2
    assert 'RFC' in trello_tasks[0]['desc']