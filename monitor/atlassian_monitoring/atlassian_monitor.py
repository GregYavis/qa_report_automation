import datetime
import json
import logging
from datetime import datetime

from django.db import IntegrityError

from confluence_table_template import issue_report_template
from monitor.models import Issue
from .base import AtlassianConfig
from .. import models

logger = logging.getLogger('django')


class AtlassianMonitor(AtlassianConfig):

    def __init__(self, request):
        super(AtlassianMonitor, self).__init__()

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
                                    body=issue_report_template(self.issue_key),
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




