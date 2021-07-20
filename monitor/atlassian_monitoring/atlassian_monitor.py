import json
import logging

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

    def issue(self):
        return Issue.objects.get(issue_key=self.issue_key)

    def get_issue_key(self):
        issue_key = self.request['issue']['key']
        return issue_key

    def confluence_link(self, confluence_id):
        return ''.join([self.confluence_viewpage, str(confluence_id)])

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
            logger.info(f'Задача {self.issue_key} уже занесена в БД')

    def check_and_update_issue(self):
        """
        Достаем таску из ДБ, если ее там нету, то она ранее не обрабатывалась
        Задач по webhookEvent = issue_updated будет много на старте,
        поэтому их тоже надо добавлять в ДБ вылавливая по exception
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
        if self.confluence.page_exists(space="AT", title=self.confluence_title.format(self.issue_key)):
            return self.confluence.get_page_by_title(space="AT",
                                                     title=self.confluence_title.format(self.issue_key))['id']
        else:
            return None

    def set_issue_confluence_id(self):
        logger.info(f'Добавлен confluence_id отчета задачи {self.issue_key}')
        issue = self.issue()
        issue.confluence_id = self.confluence_page_id()
        issue.save()

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

    def create_report(self):
        """
        Если в ДБ нет id статьи и в конфе нет статьи с тестированием задачи - создаем её.
        Если нет только айди - записываем его в ДБ,
        Если id есть - возвращаемся.
        """
        issue = self.issue()
        if not issue.confluence_id and not self.confluence_page_id():
            self._create_article()
        elif not issue.confluence_id and self.confluence_page_id():
            self.set_issue_confluence_id()
        elif issue.confluence_id:
            return

    def _create_article(self):
        logger.info(f'Создана статья с шаблоном для отчета по тестированию задачи {self.issue_key}')
        self.confluence.create_page(space='AT',
                                    title=self.confluence_title.format(self.issue_key),
                                    body=issue_report_template(self.issue_key),
                                    parent_id=self.qa_reports_page_id)
        self.set_issue_confluence_id()
        # Создать линку на созданную статью к задаче в jira
        issue = self.issue()
        self.jira.create_or_update_issue_remote_links(issue_key=self.issue_key,
                                                      link_url=self.confluence_link(issue.confluence_id),
                                                      title=self.confluence_title.format(self.issue_key))
