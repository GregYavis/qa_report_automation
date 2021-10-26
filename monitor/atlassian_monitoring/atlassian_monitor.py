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
        self.issue_url = ''.join([self.JIRA_BASE_URL, "browse/", self.issue_key])

        self.jira_issue_status = self.get_issue_status()
        self.jira_release_name = self.get_release_name()
        self.jira_issue_summary = self.get_issue_summary()
        self.jira_issue_event = self.request['webhookEvent']

    def issue(self):
        return Issue.objects.get(issue_key=self.issue_key)

    def get_issue_key(self):
        issue_key = self.request['issue']['key']
        return issue_key


    def check_and_update_issue(self):
        """
        Достаем таску из ДБ, если ее там нету, то она ранее не обрабатывалась
        Задач по webhookEvent = issue_updated будет много на старте,
        поэтому их тоже надо добавлять в ДБ вылавливая по exception
        """
        try:
            issue = self.issue()
            logger.info(f'Проверка задачи {issue.issue_key} на обновление статуса/наименования/релиза')
            confluence_id = self.get_confluence_page_id(title=self.confluence_title.format(issue.issue_key))
            if self.jira_release_name != issue.release_name:
                issue.release_report = False
                issue.release_name = self.jira_release_name
                issue.save()
            if self.jira_issue_summary != issue.issue_summary or \
                    self.jira_issue_status != issue.issue_status or \
                    confluence_id != issue.confluence_id:
                self.update_issue(self.issue_key,
                                  self.jira_issue_summary,
                                  self.jira_issue_status,
                                  self.jira_release_name,
                                  confluence_id)

        except models.Issue.DoesNotExist:
            logger.info('Создание записи для обновленной задачи еще не представленной в БД')
            try:
                logger.info(f'Создана задача {self.issue_key}. Запись в БД')
                self.save_issue(issue_key=self.issue_key,
                                issue_summary=self.jira_issue_summary,
                                release_name=self.jira_release_name,
                                issue_status=self.jira_issue_status)
            except IntegrityError:
                logger.info(f'Задача {self.issue_key} уже занесена в БД')


    def set_issue_confluence_id(self):
        issue = self.issue()
        issue.confluence_id = self.get_confluence_page_id(title=self.confluence_title.format(issue.issue_key))
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
        if not issue.confluence_id and not self.report_exists(self.issue_key):
            self._create_article_linked_with_task()
        elif not issue.confluence_id and self.report_exists(self.issue_key):
            logger.info(f'Задача уже имеет отчет о тестировании. Добавлен confluence_id отчета задачи {self.issue_key}')
            self.set_issue_confluence_id()
        elif issue.confluence_id:
            logger.info(f'Задача уже имеет отчет о тестировании и прикрепленную на него ссылку')
            return

    def _create_article_linked_with_task(self):
        logger.info(f'Создана статья с шаблоном для отчета по тестированию задачи {self.issue_key}')
        self.confluence.create_page(space='AT',
                                    title=self.confluence_title.format(self.issue_key),
                                    body=issue_report_template(self.issue_key),
                                    parent_id=self.qa_reports_page_id)
        self.set_issue_confluence_id()
        # Создать линку на созданную статью к задаче в jira
        logger.info(f'Прикрепляем на отчет о тестировании к задаче {self.issue_key}.')
        self.create_link(issue=self.issue())
