from django.test import TestCase
from atlassian import Confluence
import json
import os
import logging
from atlassian import Confluence
from atlassian import Jira
from confluence_table_template import report_template
from enum import Enum

# Create your tests here.

"""
Для каждой задачи в статусе READY
проверяем нет ли для неё отчета в конфлю,
если нету создаем,
"""


# print(self.confluence.get_page_space(37127258))

class IssueStates(Enum):
    READY_FOR_QA = 'Ready for QA'
    PASSED_QA = 'Passed QA'
    IN_REGRESSION_TEST = 'In regression test'
    READY_FOR_RELEASE = 'Ready for release'
    RELEASED = 'Released to production'
    IN_DEVELOPMENT = 'In development'


class AtlassianMonitor:
    ROOT_PATH = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    CONFIG_PATH = os.path.join(ROOT_PATH, 'config.json')
    # Шаблон запроса задач в статусе Ready for QA
    READY_FOR_QA_QUERY = 'project = 4Slovo AND status = "Ready for release" ORDER BY priority DESC'

    def __init__(self):
        self.config = json.load(open(self.CONFIG_PATH))
        self.jira = Jira(url=self.config["JIRA_URL"],
                         username=self.config["USERNAME"],
                         password=self.config["PASSWORD"])
        self.confluence = Confluence(url=self.config["CONFLUENCE_URL"],
                                     username=self.config["USERNAME"],
                                     password=self.config["PASSWORD"])
        self.issue_states = IssueStates
        self.tasks = []

    def _possible_states(self):
        return [e.value for e in self.issue_states if e != self.issue_states.IN_DEVELOPMENT]

    @staticmethod
    def __confluence_mentions_in_links(links):
        return [link for link in links if 'name' in link['application'] and 'confluence' in link['object']['url']]

    def jira_ready_for_qa_monitoring(self):
        data = self.jira.jql(self.READY_FOR_QA_QUERY)
        # print(data)
        #print(self._possible_states())
        for issue in data["issues"]:
            #print(issue['key'], self.jira.issue_field_value(issue['key'], 'status')['name'])
            self.tasks.append(issue['key'])
            links = self.jira.get_issue_remote_links(issue['id'])
            # Условие для создания статьи с шаблоном для отчета тестирования
            #print(links[0]['object']['title'])
            if not any(self.__confluence_mentions_in_links(links)):
                # Занести в SQLite

                print(self.jira.issue_field_value(key=issue['key'], field='summary'))
        #print(self.tasks)

        # return self.tasks

    # Получить имя релиза
    def get_release_name(self, issue_key):
        issue = self.jira.issue(key=issue_key)
        # print(issue)
        release = self.jira.issue_field_value(issue['key'], 'fixVersions')[0]['name']

        return release

    def confluence_monitoring(self):
        confluence = Confluence(url='https://confluence.4slovo.ru/',
                                username='g.kozlov',
                                password='Khamul_54321')
        issues = self.tasks
        for issue in issues:
            if not confluence.page_exists(space="AT", title=f'{issue}. Отчет о тестировании'):
                print('No report')
                # Создаем шаблон отчета
                #self.confluence.create_page(space='AT',
                #                            # title = 'f'{issue.issue_key}. Отчет о тестировании'',
                #                            title='Testing At-176/3 task, need to delete',
                #                            body=report_template(issue_key=issue,
                #                                                 issue_url='https://jira.4slovo.ru/browse/' + issue,
                #                                                 issue_status=self.jira.issue_field_value(issue, 'status')['name'],
                #                                                 issue_summary=self.jira.issue_field_value(key=issue,
                #                                                                                      field='summary')),
                #                            # parent_id=MUSORKA,
                #                            parent_id=37127275)


if __name__ == '__main__':
    a = AtlassianMonitor()
    a.jira_ready_for_qa_monitoring()
    # print(len('Released to production'))
    #print(a.get_release_name('SLOV-6006'))
    # print(a._possible_states())
    #a.confluence_monitoring()
