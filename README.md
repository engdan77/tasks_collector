##Background
The purpose with this project was to address the headache of collecting and organizing the tasks are/have worked with.
These tasks spread across different platforms such as Outlook, Jira, Trello and so forth and felt like I had to structure and
 store these into a database and being able to create some charts based on this. 

## Demo

[![asciicast](https://asciinema.org/a/tsxZmDb4NIBDylFUQHSZ82mVR.svg)](https://asciinema.org/a/tsxZmDb4NIBDylFUQHSZ82mVR)

##Installation

Install CopyQ according to https://hluk.github.io/CopyQ/

```
# install -r requirements.txt
```

##Usage
In general you only need to pass the sqlite database where you'd like to store it.

####Collect
#####Outlook
When passing --outlook argument you just need to make sure you've selected all Outlook-tasks including those completed.
While using Outlook you can add the following naming convention of Outlooks "Categories" 

(client1)
(client2)
(client3)
...

for giving you possibility to assign clients associated with task.

{project1}
{project2}
{project3}
...

for assigning the task specific project.

#####Jira
The script will use the username@jiraserver supplied to detect all tasks that are assigned to you and collect their most recent details into the database.

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

######Credentials

Currently use keyring to allow you to store credentials locally not being exposed.
First time you run it will prompt you for password.

####Report
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

####Cleanup
This is useful if for example ownership changes of tickets in Jira end you'd like to close them in your report.
```
usage: tasks_collector.py cleanup [-h] [--before DAYS]
                                  [--loglevel {INFO,DEBUG}]
                                  sqlite_database

positional arguments:
  sqlite_database       name of sqlite to export/update to

optional arguments:
  -h, --help            show this help message and exit
  --before DAYS         tickets before this number of days back to be closed
  --loglevel {INFO,DEBUG}

```