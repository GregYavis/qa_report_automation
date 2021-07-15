import json
import json
import os
from enum import Enum

from atlassian import Confluence
from atlassian import Jira



class IssueStates(Enum):
    READY_FOR_QA = 'Ready for QA'
    PASSED_QA = 'Passed QA'
    IN_REGRESSION_TEST = 'In regression test'
    READY_FOR_RELEASE = 'Ready for release'
    RELEASED = 'Released to production'

class AtlassianConfig:
    JIRA_ISSUE_UPDATED = 'jira:issue_updated'
    JIRA_ISSUE_CREATED = 'jira:issue_created'
    ROOT_PATH = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    CONFIG_PATH = os.path.join(ROOT_PATH, 'config.json')

    QA_QUERY = 'project = 4Slovo AND status = "Ready for QA" or status = "Passed QA" or status ' \
               '= "In regression test" or status = "Ready for release" ORDER BY priority DESC'

    confluence_viewpage = 'https://confluence.4slovo.ru/pages/viewpage.action?pageId='
    # confluence_title = '{}. Отчет о тестировании'
    qa_reports_page_id = 37127275

    def __init__(self):
        self.config = json.load(open(self.CONFIG_PATH))
        self.jira = Jira(url=self.config["JIRA_URL"],
                         username=self.config["USERNAME"],
                         password=self.config["PASSWORD"])
        self.confluence = Confluence(url=self.config["CONFLUENCE_URL"],
                                     username=self.config["USERNAME"],
                                     password=self.config["PASSWORD"])

        self.issue_states = IssueStates
