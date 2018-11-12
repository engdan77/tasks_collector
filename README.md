

**Installation**

```
# cd src && pip install -r requirements.txt
```

Usage

```
# python tasks_collector.py collect --help
usage: tasks_collector.py collect [-h] [--outlook] [--jira JIRA]
                                  [--loglevel {INFO,DEBUG}]
                                  sqlite_database

positional arguments:
  sqlite_database       name of sqlite to export/update to

optional arguments:
  -h, --help            show this help message and exit
  --outlook
  --jira JIRA           username@jiraserver
  --loglevel {INFO,DEBUG}
```

```
# python tasks_collector.py report --help
usage: tasks_collector.py report [-h] [--days number_of_days_in_past]
                                 [--loglevel {INFO,DEBUG}]
                                 sqlite_database

positional arguments:
  sqlite_database       name of sqlite to get data from

optional arguments:
  -h, --help            show this help message and exit
  --days number_of_days_in_past
                        Number of days to cover in the report
  --loglevel {INFO,DEBUG}
```