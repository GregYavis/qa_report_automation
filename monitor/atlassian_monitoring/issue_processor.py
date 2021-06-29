import json
import logging
import os
from enum import Enum
from nested_lookup import nested_lookup
from atlassian import Confluence
from atlassian import Jira

from monitor.models import Issue

logging.basicConfig(filename='cron.log')
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
file = logging.FileHandler('cron.log')
file.setLevel(logging.INFO)
# formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logger.addHandler(file)


class IssueStates(Enum):
    READY_FOR_QA = 'Ready for QA'
    PASSED_QA = 'Passed QA'
    IN_REGRESSION_TEST = 'In regression test'
    READY_FOR_RELEASE = 'Ready for release'
    RELEASED = 'Released to production'
    IN_DEVELOPMENT = 'In development'


class IssueProcessingBasics:
    ROOT_PATH = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    CONFIG_PATH = os.path.join(ROOT_PATH, 'config.json')
    # Шаблон запроса задач в статусе Ready for QA
    # READY_FOR_QA_QUERY = 'project = 4Slovo AND status = "Ready for QA" ORDER BY priority DESC'
    QA_QUERY = 'project = 4Slovo AND status = "Ready for QA" or status = "Passed QA" or status ' \
               '= "In regression test" or status = "Ready for release" ORDER BY priority DESC'

    confluence_viewpage = 'https://confluence.4slovo.ru/pages/viewpage.action?pageId='

    def __init__(self):
        self.config = json.load(open(self.CONFIG_PATH))
        self.jira = Jira(url=self.config["JIRA_URL"],
                         username=self.config["USERNAME"],
                         password=self.config["PASSWORD"])
        self.confluence = Confluence(url=self.config["CONFLUENCE_URL"],
                                     username=self.config["USERNAME"],
                                     password=self.config["PASSWORD"])
        self.issue_states = IssueStates

    def _possible_states(self):
        return [e.value for e in self.issue_states if e != self.issue_states.IN_DEVELOPMENT]

    @staticmethod
    def _confluence_mentions_in_links(links):
        return [link for link in links if 'name' in link['application'] and 'confluence' in link['object']['url']]


    def find_confluence_mentions(self, doc):
        #[url for url in self.find_confluence_mentions(key='url', doc=links) if self.confluence_viewpage in url]
        print(nested_lookup('url', doc))
        #return nested_lookup(key, doc)
        return [url for url in nested_lookup('url', doc) if self.confluence_viewpage in url]


    @staticmethod
    def _issue_already_processed(issue_key):
        return Issue.objects.filter(issue_key=issue_key)

    def _get_issue_status(self, issue_key):
        return self.jira.issue_field_value(issue_key, 'status')['name']

    @staticmethod
    def _update_issue_status(issue_key, issue_status):
        update_issue = Issue.objects.get(issue_key=issue_key)
        update_issue.issue_status = issue_status
        update_issue.save()
        logger.info(f'Update status for {issue_key} to "{issue_status}".')

    def get_release_name(self, issue_key):
        release_name = self.jira.issue_field_value(issue_key, 'fixVersions')
        if release_name:
            return release_name[0]['name']
        else:
            return None

    def get_issue_summary(self, issue_key):
        return self.jira.issue_field_value(key=issue_key, field='summary')

    @staticmethod
    def set_issue_confluence_id(issue_key, confluence_id):
        update_issue = Issue.objects.get(issue_key=issue_key)
        update_issue.confluence_id = confluence_id
        update_issue.save()
        logger.info(f'Set confluence ID for {issue_key} - "{confluence_id}".')

    @staticmethod
    def update_issue_release_name(issue_key, release):
        update_issue = Issue.objects.get(issue_key=issue_key)
        update_issue.release_name = release
        update_issue.save()
        logger.info(f'Update release name for {issue_key} to "{release}".')

    def _get_current_releases(self):
        released_issues = Issue.objects.filter(issue_status=
                                               self.issue_states.READY_FOR_RELEASE.value, release_report=False)
        return set(release.release_name for release in released_issues)

    def get_current_releases_info(self):
        info = {release_name: {issue.issue_key: issue.issue_status
                               for issue in Issue.objects.filter(release_name=release_name)}
                for release_name in self._get_current_releases()}
        return info


