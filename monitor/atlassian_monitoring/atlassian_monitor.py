import datetime
import json
import logging
import os
from enum import Enum

from atlassian import Confluence
from atlassian import Jira
from django.db import IntegrityError

from confluence_table_template import confluence_body_template
from monitor.models import Issue
from .. import models

logger = logging.getLogger('django')


class IssueStates(Enum):
    READY_FOR_QA = 'Ready for QA'
    PASSED_QA = 'Passed QA'
    IN_REGRESSION_TEST = 'In regression test'
    READY_FOR_RELEASE = 'Ready for release'
    RELEASED = 'Released to production'


class FeatureReleases:
    issue_states = IssueStates

    def get_feature_releases_info(self):
        issues_to_release = Issue.objects.filter(confluence_id__isnull=False,
                                                 release_report=False,
                                                 release_name__isnull=False)
        feature_releases = set(issue.release_name for issue in issues_to_release if
                               issue.issue_status in self._possible_states())
        info = {release_name: {issue.issue_key: issue.issue_status
                               for issue in Issue.objects.filter(release_name=release_name)}
                for release_name in feature_releases}
        return info

    def _possible_states(self):
        return [e.value for e in self.issue_states if e != self.issue_states.RELEASED]


class AtlassianMonitor:
    JIRA_ISSUE_UPDATED = 'jira:issue_updated'
    JIRA_ISSUE_CREATED = 'jira:issue_created'
    ROOT_PATH = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    CONFIG_PATH = os.path.join(ROOT_PATH, 'config.json')

    QA_QUERY = 'project = 4Slovo AND status = "Ready for QA" or status = "Passed QA" or status ' \
               '= "In regression test" or status = "Ready for release" ORDER BY priority DESC'

    confluence_viewpage = 'https://confluence.4slovo.ru/pages/viewpage.action?pageId='
    # confluence_title = '{}. Отчет о тестировании'
    qa_reports_page_id = 37127275

    def __init__(self, request):
        self.config = json.load(open(self.CONFIG_PATH))
        self.jira = Jira(url=self.config["JIRA_URL"],
                         username=self.config["USERNAME"],
                         password=self.config["PASSWORD"])
        self.confluence = Confluence(url=self.config["CONFLUENCE_URL"],
                                     username=self.config["USERNAME"],
                                     password=self.config["PASSWORD"])

        self.issue_states = IssueStates

        self.request = json.loads(request.body.decode('utf-8'))
        self.issue_key = self.get_issue_key()
        self.issue_url = ''.join(['https://jira.4slovo.ru/browse/', self.issue_key])

        self.issue_status = self.get_issue_status()
        self.release_name = self.get_release_name()
        self.issue_summary = self.get_issue_summary()
        self.issue_event = self.request['webhookEvent']
        print(self.issue_key)
        print(self.issue_status)
        print(self.release_name)
        print(self.issue_summary)

    def issue(self):
        return Issue.objects.get(issue_key=self.issue_key)

    def get_issue_key(self):
        issue_key = self.request['issue']['key']
        return issue_key

    def confluence_link(self, confluence_id):
        return ''.join([self.confluence_viewpage, str(confluence_id)])

    def confluence_title(self):
        return f'{self.issue_key}. Отчет о тестировании'

    def get_issue_data(self):
        return self.issue_summary, self.release_name, self.issue_status

    def save_issue(self):
        try:
            Issue.objects.create(issue_key=self.issue_key,
                                 jira_url=self.issue_url,
                                 issue_summary=self.issue_summary,
                                 issue_status=self.issue_status,
                                 confluence_id=self.confluence_page_id())
        except IntegrityError:
            logger.info(f'Try insert issue that exists in DB: {self.issue_key}')

    def check_and_update_issue(self):
        """
        Достаем таску из ДБ, если ее там нету, то она ранее не обрабатывалась
        Задач по webhookEvent = issue_updated будет много на старте,
        поэтому их тоже надо добавлять в ДБ вылавливая по exception
        :return:
        """
        try:
            issue = self.issue()
            logger.info('Check issue for updates')

            if self.issue_summary != issue.issue_summary or \
                    self.issue_status != issue.issue_status or \
                    self.release_name != issue.release_name or \
                    self.confluence_page_id():
                self.update_issue(self.issue_summary, self.issue_status, self.release_name, self.confluence_page_id())

        except models.Issue.DoesNotExist:
            logger.info('Create database entry for updated issue that not writen in DB')
            self.save_issue()

    def update_issue(self, issue_summary, issue_status, release_name, confluence_id):
        issue = self.issue()
        issue.issue_summary = issue_summary
        issue.issue_status = issue_status
        issue.release_name = release_name
        issue.confluence_id = confluence_id
        issue.save()

    def confluence_page_id(self):
        if self.confluence.page_exists(space="AT", title=self.confluence_title().format(self.issue_key)):
            return self.confluence.get_page_by_title(space="AT", title=self.confluence_title().format(self.issue_key))[
                'id']
        else:
            return None

    def set_issue_confluence_id(self):
        issue = self.issue()
        issue.confluence_id = self.confluence_page_id()
        issue.save()
        logger.info(f'Set confluence ID for {issue.issue_key} - "{issue.confluence_id}".')

    def get_issue_summary(self):
        return self.request['issue']['fields']['summary']

    def get_issue_status(self):
        return self.request['issue']['fields']['status']['name']

    def issue_ready_for_qa(self):
        return self.get_issue_status() == self.issue_states.READY_FOR_QA.value

    def issue_is_rc(self):
        return self.request['issue']['fields']['issuetype']['name'] == 'RC'

    def get_release_name(self):
        release_name = self.request['issue']['fields']['fixVersions']
        if release_name:
            return release_name[0]['name']
        else:
            return None

    def report_template(self):
        return confluence_body_template(issue_key=self.issue_key,
                                        issue_url=self.issue_url,
                                        issue_status=self.issue_status,
                                        issue_summary=self.issue_summary)

    # def confluence_report_exists(self):
    #    print(self.confluence.get_page_by_title(space="AT", title=self.confluence_title().format(self.issue_key)))
    #    return self.confluence.page_exists(space="AT", title=self.confluence_title().format(self.issue_key))

    def create_report(self):
        """
        Если в ДБ нет id статьи и в конфе нет статьи с тестированием задачи - создаем её.
        Если нет только айди - записываем его в ДБ,
        Если id есть - возвращаемся.
        :return:
        """
        issue = self.issue()
        if not issue.confluence_id and not self.confluence_page_id():
            self._create_article()
        elif not issue.confluence_id and self.confluence_page_id():
            logger.info(f'Update issue {self.issue_key} in DB, insert confluence_id of article')
            self.set_issue_confluence_id()
        elif issue.confluence_id:
            return

    def _create_article(self):
        logger.info(f'Create confluence article for {self.issue_key}')
        self.confluence.create_page(space='AT',
                                    title=self.confluence_title(),
                                    body=self.report_template(),
                                    parent_id=self.qa_reports_page_id)
        self.set_issue_confluence_id()

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
