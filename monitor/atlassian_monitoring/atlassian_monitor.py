import json
import logging
import logging.handlers
import multiprocessing
import datetime
from enum import Enum

from django.db import IntegrityError

from confluence_table_template import confluence_body_template
from .issue_processor import IssueProcessingBasics
from monitor.models import Issue
import json
import logging
import os
from enum import Enum
from nested_lookup import nested_lookup
from atlassian import Confluence
from atlassian import Jira

logger = logging.getLogger('django')


class FeatureReleases:

    @staticmethod
    def get_current_releases():
        # If issue has report in confluence and not release reported - issue in near feature releases
        issues_to_release = Issue.objects.filter(confluence_id=not None, release_report=False)
        return set(release.release_name for release in issues_to_release)

    def get_feature_releases_info(self):
        info = {release_name: {issue.issue_key: issue.issue_status
                               for issue in Issue.objects.filter(release_name=release_name)}
                for release_name in self.get_current_releases()}
        return info


class IssueStates(Enum):
    READY_FOR_QA = 'Ready for QA'
    PASSED_QA = 'Passed QA'
    IN_REGRESSION_TEST = 'In regression test'
    READY_FOR_RELEASE = 'Ready for release'
    RELEASED = 'Released to production'
    IN_DEVELOPMENT = 'In development'


class AtlassianMonitor:
    JIRA_ISSUE_UPDATED = 'jira:issue_updated'
    JIRA_ISSUE_CREATED = 'jira:issue_created'
    ROOT_PATH = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    CONFIG_PATH = os.path.join(ROOT_PATH, 'config.json')

    QA_QUERY = 'project = 4Slovo AND status = "Ready for QA" or status = "Passed QA" or status ' \
               '= "In regression test" or status = "Ready for release" ORDER BY priority DESC'

    confluence_viewpage = 'https://confluence.4slovo.ru/pages/viewpage.action?pageId='
    jira_issue_url_template = 'https://jira.4slovo.ru/browse/'
    confluence_title = '{}. Отчет о тестировании'

    def __init__(self, request):
        self.config = json.load(open(self.CONFIG_PATH))
        self.jira = Jira(url=self.config["JIRA_URL"],
                         username=self.config["USERNAME"],
                         password=self.config["PASSWORD"])
        self.confluence = Confluence(url=self.config["CONFLUENCE_URL"],
                                     username=self.config["USERNAME"],
                                     password=self.config["PASSWORD"])

        self.issue_states = IssueStates

        self.decoded_request = json.loads(request.body.decode('utf-8'))
        self.issue_key = self.get_issue_key()

        self.issue_summary = self.get_issue_summary()
        self.issue_status = self.get_issue_status()
        self.release_name = self.get_release_name()

        self.issue_event = self.decoded_request['webhookEvent']

    def get_issue_key(self):
        issue_key = self.decoded_request['issue']['key']
        return issue_key

    def confluence_link(self, confluence_id):
        return ''.join([self.confluence_viewpage, str(confluence_id)])

    # Сейчас используется для тестирования в кроне, при переходе на вебхук - убрать

    def get_issue_data(self):
        return self.issue_summary, self.release_name, self.issue_status

    def insert_issue_to_database(self, issue_summary, release_name, issue_status):
        try:
            Issue.objects.create(issue_key=self.issue_key,
                                 jira_url=self.issue_url,
                                 issue_summary=issue_summary,
                                 release_name=release_name,
                                 issue_status=issue_status)
        except IntegrityError:
            logger.info(f'Try insert issue that exists in DB: {self.issue_key}')

    def check_and_update_issue(self):
        # check - summary, issue, status, release_name
        issue = Issue.objects.get(issue_key=self.issue_key)
        if self.issue_summary != issue.issue_summary or \
                self.issue_status != issue.issue_status or \
                self.release_name != issue.release_name:
            self.update_issue(issue, self.issue_summary, self.issue_status, self.release_name)

    @staticmethod
    def update_issue(issue, issue_summary, issue_status, release_name):
        issue.issue_summary = issue_summary
        issue.issue_status = issue_status
        issue.release_name = release_name
        issue.save()

    def get_issue_summary(self):
        return self.jira.issue_field_value(key=self.issue_key, field='summary')

    def get_issue_status(self):
        #return self.decoded_request['status']['name']
        return self.jira.issue_field_value(self.issue_key, 'status')['name']

    def issue_ready_for_qa(self):
        return self.get_issue_status() == self.issue_states.READY_FOR_QA.value

    def issue_is_rc(self):
        return self.jira.issue_field_value(self.issue_key, 'issuetype')['name'] == 'RC'

    def issue_url(self):
        return ''.join([self.jira_issue_url_template, self.issue_key])

    def get_release_name(self):
        release_name = self.jira.issue_field_value(self.issue_key, 'fixVersions')
        if release_name:
            return release_name[0]['name']
        else:
            return None

    def create_confluence_article(self):
        print("CREATE ARRTICLE")
        # return
        #self.confluence.create_page(space='AT',
        #                            title=self.confluence_title.format(self.issue_key),
         #                           body=confluence_body_template())

    #def report_template(self):
    #    return confluence_body_template(issue_key=self.issue_key,
     #                                   issue_url=self.issue_url(),
    #                                    issue_status=self.issue_status)

    def move_page(self):
        # page_id = self.confluence.get_page_by_title()
        # need get current year, release that task relate to,
        release_name = 'ru.6.3.25'
        year_release = datetime.datetime.today().year
        # print(year_release)
        _release_id = self.confluence.get_page_by_title(space="AT", title=f'Релиз {release_name} Отчет о тестировании')
        # print(_release_id)
        updated_issue = Issue.objects.get(issue_key='SLOV-6950')
        page_id = updated_issue.confluence_id
        confluence_title = f'{updated_issue.issue_key}. Отчет о тестировании'
        self.confluence.update_page(page_id=page_id, title=confluence_title, parent_id=_release_id, )

    def all_release_tasks_ready(self, release_name):
        # get current state of tasks by
        # self.check_and_update_issues()
        ready_tasks = Issue.objects.filter(release_name=release_name,
                                           issue_status=self.issue_states.READY_FOR_RELEASE.value)
        all_release_tasks = Issue.objects.filter(release_name=release_name)
        return len(ready_tasks) == len(all_release_tasks)

    # For webhook -
    # Scope - project = 4Slovo
    # Events - Issue Updated, Issue Created ...
    # Send post request to work machine with server
    # process a request, depending on request data launch update_issue,

    # a.confluence_monitoring("SLOV-6936")
