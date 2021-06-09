import os
from atlassian import Confluence
from atlassian import Jira

"""
python manage.py crontab add
python manage.py crontab run cc96dca57171b6521384fa538a69f69d
python manage.py crontab remove

"""

def do():
    with open('/home/greg/PycharmProjects/qa_report/sample.txt', 'a') as f:
        f.write('NEW LINE\n')
        f.close()