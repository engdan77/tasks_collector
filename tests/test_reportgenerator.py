from tasks_collector.reportgenerator.api import dict_keys_to_ymd, render_task, \
    all_values, count_items, get_lowest_value, create_concurrent_list
import pytest


@pytest.fixture
def setup_invalid_date_task():
    t = {'subject': 'Foo Bar',
         'start_date': '2019-01-10',
         'close_date': '2019/01/10',
         'due_date': '1 january 2019',
         'modified_date': '2019-02-15 15:00'}
    return t


def test_dict_keys_to_ymd(setup_invalid_date_task):
    t = setup_invalid_date_task
    expected = {'close_date': '2019-01-10',
                'due_date': '2019-01-01',
                'modified_date': '2019-02-15',
                'start_date': '2019-01-10',
                'subject': 'Foo Bar'}
    result = dict_keys_to_ymd(t, ['start_date', 'close_date', 'due_date', 'modified_date'])
    assert result == expected


def test_render_task():
    t = render_task('my_client', 'my_category', 'my_subject', status='open')
    assert 'my_client' in t


@pytest.fixture
def setup_list_dict():
    return [{'name': 'Foo', 'value': 'x', 'number': 20}, {'name': 'Bar', 'value': 'y', 'number': 40}]


def test_all_values(setup_list_dict):
    assert all_values(setup_list_dict, key='name') == ['Bar', 'Foo']


def test_count_items(setup_list_dict):
    assert count_items(setup_list_dict, {'name': 'Foo'}) == 1


def test_get_lowest_value(setup_list_dict):
    assert get_lowest_value(setup_list_dict, 'number') == 40


@pytest.fixture
def setup_generic_task():
    return [{'name': 'Foo Bar 1',
             'start_date': '2019-01-10',
             'close_date': '2019-01-15',
             'client_category': 'my_category_1'},
            {'name': 'Foo Bar 2',
             'start_date': '2019-02-10',
             'close_date': '2019-02-15',
             'client_category': 'my_category_2'},
            {'name': 'Foo Bar 3',
             'start_date': '2019-03-10',
             'close_date': '2019-03-15',
             'client_category': 'my_category_3'}
            ]


def test_create_concurrent_list(setup_generic_task):
    expected = [
         {'date': '2019-01-10',
          'my_category_1': 1,
          'my_category_2': 0,
          'my_category_3': 0},
         {'date': '2019-01-15',
          'my_category_1': 0,
          'my_category_2': 0,
          'my_category_3': 0},
         {'date': '2019-02-10',
          'my_category_1': 0,
          'my_category_2': 1,
          'my_category_3': 0},
         {'date': '2019-02-15',
          'my_category_1': 0,
          'my_category_2': 0,
          'my_category_3': 0},
         {'date': '2019-03-10',
          'my_category_1': 0,
          'my_category_2': 0,
          'my_category_3': 1},
         {'date': '2019-03-15',
          'my_category_1': 0,
          'my_category_2': 0,
          'my_category_3': 0}
    ]
    result = create_concurrent_list(setup_generic_task, name_key='client_category')
    assert result == expected
