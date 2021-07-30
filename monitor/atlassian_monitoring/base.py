import json
import json
import os
from enum import Enum
from monitor.models import Issue
from atlassian import Confluence
from atlassian import Jira


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
    REOPEN = 'Reopen'


class AtlassianConfig:
    JIRA_ISSUE_UPDATED = 'jira:issue_updated'
    JIRA_ISSUE_CREATED = 'jira:issue_created'
    ROOT_PATH = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    CONFIG_PATH = os.path.join(ROOT_PATH, 'config.json')

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

    def issue_confluence_id(self, links):
        try:
            return self.confluence_mentions_in_links(links)[0]['object']['url'].split('=')[1]
        except IndexError:
            return None

    @staticmethod
    def confluence_mentions_in_links(links):
        return [link for link in links if 'name' in link['application'] and 'confluence' in link['object']['url']]

    def release_name(self, issue_key):
        release_name = self.jira.issue_field_value(issue_key, 'fixVersions')
        if release_name:
            return release_name[0]['name']
        else:
            return None

    def issue_status(self, issue_key):
        return self.jira.issue_field_value(issue_key, 'status')['name']

    def issue_summary(self, issue_key):
        return self.jira.issue_field_value(key=issue_key, field='summary')

    def confluence_page(self, title):
        return self.confluence.get_page_by_title(space='AT', title=title)

    def create_link(self, issue):
        new_article_confluence_id = self.confluence_page(title=self.confluence_title.format(issue.issue_key))['id']
        self.jira.create_or_update_issue_remote_links(issue_key=issue.issue_key,
                                                      link_url=''.join(
                                                          [self.confluence_viewpage, str(new_article_confluence_id)]),
                                                      title=self.confluence_title.format(issue.issue_key))