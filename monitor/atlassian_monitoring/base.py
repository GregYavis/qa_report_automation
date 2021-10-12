import json
import logging
import os
from enum import Enum
from monitor.models import Issue
from atlassian import Confluence
from atlassian import Jira
from nested_lookup import nested_lookup

logger = logging.getLogger('django')


class IssueStates(Enum):
    READY_FOR_QA = 'Ready for QA'
    PASSED_QA = 'Passed QA'
    IN_REGRESSION_TEST = 'In regression test'
    READY_FOR_RELEASE = 'Ready for release'
    RELEASED = 'Released to production'
    CLOSED = 'Closed'
    CLOSED_RU = 'Закрыт'
    FIXED = 'Fixed'
    FIXED_RU = 'Готово'
    IN_QA = 'In QA'
    OPEN = 'Open'
    REOPEN = 'Reopened'
    IN_DEVELOPMENT = 'In development'
    BLOCKED = 'Blocked / on hold'
    READY_FOR_REVIEW = 'Ready for review'
    READY_FOR_TECHNICAL_SOLUTION_REVIEW = 'Ready for technical solution review'
    READY_FOR_DEVELOPMENT = 'Ready for development'
    TECHNICAL_SOLUTION = 'Technical solution'
    IN_PROGRESS = 'In Progress'


class AtlassianConfig:
    JIRA_ISSUE_UPDATED = 'jira:issue_updated'
    JIRA_ISSUE_CREATED = 'jira:issue_created'
    ROOT_PATH = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    CONFIG_PATH = os.path.join(ROOT_PATH, 'config.json')
    JIRA_BASE_URL = json.load(open(CONFIG_PATH))['JIRA_URL']
    QA_QUERY = 'project = 4Slovo AND status = "Ready for QA" or status = "Passed QA" or status ' \
               '= "In regression test" or status = "Ready for release" ORDER BY priority DESC'

    confluence_viewpage = 'https://confluence.4slovo.ru/pages/viewpage.action?pageId='

    qa_reports_page_id = 37127275
    confluence_title = '{}. Отчет о тестировании'

    def __init__(self):
        self.config = json.load(open(self.CONFIG_PATH))
        self.jira = Jira(url=self.config["JIRA_URL"],
                         username=self.config["USERNAME"],
                         password=self.config["PASSWORD"])
        self.confluence = Confluence(url=self.config["CONFLUENCE_URL"],
                                     username=self.config["USERNAME"],
                                     password=self.config["PASSWORD"])
        self.issue_states = IssueStates

    def release_name(self, issue_key):
        release_name = self.jira.issue_field_value(key=issue_key,  field='fixVersions')
        if release_name:
            return release_name[0]['name']
        else:
            return None

    def issue_status(self, issue_key):
        return self.jira.issue_field_value(key=issue_key,  field='status')['name']

    def issue_summary(self, issue_key):
        return self.jira.issue_field_value(key=issue_key, field='summary')

    def get_confluence_page_id(self, title):
        if self.confluence.page_exists(space="AT", title=title):
            return self.confluence.get_page_by_title(space="AT", title=title)['id']
        else:
            return None

    def create_link(self, issue):
        new_article_confluence_id = self.get_confluence_page_id(title=self.confluence_title.format(issue.issue_key))
        self.jira.create_or_update_issue_remote_links(issue_key=issue.issue_key,
                                                      link_url=''.join(
                                                          [self.confluence_viewpage, str(new_article_confluence_id)]),
                                                      title=self.confluence_title.format(issue.issue_key))

    def check_report_link_in_remote_links(self, issue):
        # Проверяем ссылки на отчет о тестировании
        links = self.jira.get_issue_remote_links(issue_key=issue.issue_key)
        urls = [nested_lookup(key='url', document=link)[0] for link in links]
        if ''.join([self.confluence_viewpage, str(issue.confluence_id)]) in urls:
            return True
        else:
            return False

    @staticmethod
    def update_issue(issue_key, issue_summary, issue_status, release_name, confluence_id):
        issue = Issue.objects.get(issue_key=issue_key)
        issue.issue_summary = issue_summary
        issue.issue_status = issue_status
        issue.release_name = release_name
        issue.confluence_id = confluence_id
        issue.save()

    def report_exists(self, issue_key):
        return self.confluence.page_exists(space="AT", title=self.confluence_title.format(issue_key))

    def save_issue(self, issue_key, issue_summary, release_name, issue_status,):
        Issue.objects.create(issue_key=issue_key,
                             jira_url=''.join([self.JIRA_BASE_URL, "browse/", issue_key]),
                             issue_summary=issue_summary,
                             issue_status=issue_status,
                             release_name=release_name,
                             confluence_id=self.get_confluence_page_id(
                                 title=self.confluence_title.format(issue_key)))
