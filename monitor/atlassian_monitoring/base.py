import json
import logging
import os
from datetime import datetime
from enum import Enum

from requests import HTTPError

from confluence_table_template import issue_report_template
from monitor.models import Issue
from atlassian import Confluence
from atlassian import Jira
from nested_lookup import nested_lookup

logger = logging.getLogger('django')


class IssueStates(Enum):
    READY_FOR_QA = 'Ready for QA'
    PASSED_QA = 'Passed QA'
    IN_REGRESSION_TEST = 'In regression test'
    IN_REGRESS_TEST_RC = 'In Regress Test RC'
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
    IN_INTEGRATION_TEST = 'In integration test'


class AtlassianConfig:
    JIRA_ISSUE_UPDATED = 'jira:issue_updated'
    JIRA_ISSUE_CREATED = 'jira:issue_created'
    ROOT_PATH = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    CONFIG_PATH = os.path.join(ROOT_PATH, 'config.json')
    JIRA_BASE_URL = json.load(open(CONFIG_PATH))['JIRA_URL']
    QA_QUERY = 'project = 4Slovo AND status = "Ready for QA" ' \
               'or status = "Passed QA" ' \
               'or status = "In regression test" ' \
               'or status = "Ready for release" ' \
               'or status = "Open" ' \
               'or status = "Ready for review" ' \
               'or status = "In integration test" '\
               'or status = "Ready for technical solution review" ORDER BY priority DESC'
    ISSUES_BY_RELEASE = 'project = 4Slovo AND fixVersion = {}'
    confluence_viewpage = 'https://confluence.4slovo.ru/pages/viewpage.action?pageId={}'

    qa_reports_page_id = 37127275
    confluence_title = '{}. Отчет о тестировании'
    qa_confluence_id = 33587493

    def __init__(self):
        self.config = json.load(open(self.CONFIG_PATH))
        self.jira = Jira(url=self.config["JIRA_URL"],
                         username=self.config["USERNAME"],
                         password=self.config["PASSWORD"])
        self.confluence = Confluence(url=self.config["CONFLUENCE_URL"],
                                     username=self.config["USERNAME"],
                                     password=self.config["PASSWORD"])
        self.issue_states = IssueStates

    def qa_states(self):
        return [e.value for e in self.issue_states if e not in [self.issue_states.RELEASED,
                                                                self.issue_states.READY_FOR_QA,
                                                                self.issue_states.OPEN,
                                                                self.issue_states.REOPEN,
                                                                self.issue_states.IN_DEVELOPMENT,
                                                                self.issue_states.BLOCKED,
                                                                self.issue_states.READY_FOR_REVIEW,
                                                                self.issue_states.READY_FOR_TECHNICAL_SOLUTION_REVIEW,
                                                                self.issue_states.READY_FOR_DEVELOPMENT,
                                                                self.issue_states.TECHNICAL_SOLUTION,
                                                                self.issue_states.IN_PROGRESS
                                                                ]]

    def ready_for_report_states(self):
        return [e.value for e in self.issue_states if e not in [self.issue_states.READY_FOR_QA,
                                                                self.issue_states.REOPEN,
                                                                self.issue_states.IN_DEVELOPMENT,
                                                                self.issue_states.BLOCKED,
                                                                self.issue_states.READY_FOR_REVIEW,
                                                                self.issue_states.READY_FOR_TECHNICAL_SOLUTION_REVIEW,
                                                                self.issue_states.READY_FOR_DEVELOPMENT,
                                                                self.issue_states.TECHNICAL_SOLUTION,
                                                                self.issue_states.IN_PROGRESS,
                                                                ]]

    def release_name(self, issue_key):
        try:
            release_name = self.jira.issue_field_value(key=issue_key, field='fixVersions')
            if release_name:
                return release_name[0]['name']
            else:
                return None
        except HTTPError:
            logger.info(
                f'{datetime.now().strftime("%d/%m/%Y %H:%M:%S")} Обращение к скрытой или не существующей записи')

    def issue_status(self, issue_key):
        try:
            return self.jira.issue_field_value(key=issue_key, field='status')['name']
        except HTTPError:
            logger.info(
                f'{datetime.now().strftime("%d/%m/%Y %H:%M:%S")} Обращение к скрытой или не существующей записи')

    def issue_summary(self, issue_key):
        try:
            summary = self.jira.issue_field_value(key=issue_key, field='summary')
            return summary
        except HTTPError:
            logger.info(
                f'{datetime.now().strftime("%d/%m/%Y %H:%M:%S")} Обращение к скрытой или не существующей записи')

    def create_issue(self, issue_key):
        logger.info(f'{datetime.now().strftime("%d/%m/%Y %H:%M:%S")} Запись в БД {issue_key}.')
        self.save_issue(issue_key=issue_key,
                        issue_summary=self.issue_summary(issue_key),
                        release_name=self.release_name(issue_key),
                        issue_status=self.issue_status(issue_key))

    def create_template(self, issue_key):
        logger.info(f'{datetime.now().strftime("%d/%m/%Y %H:%M:%S")} Создание шаблона отчета для задачи {issue_key}.')
        self.confluence.create_page(space='AT',
                                    title=self.confluence_title.format(issue_key),
                                    body=issue_report_template(issue_key),
                                    parent_id=self.qa_reports_page_id)

    def get_confluence_page_id(self, title):
        if self.confluence.page_exists(space="AT", title=title):
            return self.confluence.get_page_by_title(space="AT", title=title)['id']
        else:
            return None

    def create_link(self, issue):
        try:
            if not self.check_report_link_in_remote_links(issue=issue):
                new_article_confluence_id = self.get_confluence_page_id(
                    title=self.confluence_title.format(issue.issue_key))
                self.jira.create_or_update_issue_remote_links(issue_key=issue.issue_key,
                                                              link_url=self.confluence_viewpage.format(
                                                                  str(new_article_confluence_id)),
                                                              title=self.confluence_title.format(issue.issue_key))
        except HTTPError:
            logger.info(
                f'{datetime.now().strftime("%d/%m/%Y %H:%M:%S")} Обращение к скрытой или не существующей записи')

    def check_report_link_in_remote_links(self, issue):
        # Проверяем ссылки на отчет о тестировании
        logger.info(
            f"{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}  +_+_+_+ Проверка существования линка к задаче {issue.issue_key} +_+_+_+")
        logger.info(f'EXPEXT {self.confluence_viewpage.format(str(issue.confluence_id))}')

        links = self.jira.get_issue_remote_links(issue_key=issue.issue_key)
        urls = [nested_lookup(key='url', document=link)[0] for link in links]
        logger.info(f"{datetime.now().strftime('%d/%m/%Y %H:%M:%S')} +_+_+_+{links}")
        logger.info(f"{datetime.now().strftime('%d/%m/%Y %H:%M:%S')} +_+_+_+{urls}")
        duplicate_urls = [data['object']['url'] for data in links]
        if urls.count(self.confluence_viewpage.format(str(issue.confluence_id))) > 1:
            logger.info(f':::::::::::::::::https://jira.4slovo.ru/browse/{issue.issue_key}:::::::::::::::::')
        if (self.confluence_viewpage.format(str(issue.confluence_id)) in urls) or \
                (self.confluence_viewpage.format(str(issue.confluence_id)) in duplicate_urls):
            logger.info(
                f"{datetime.now().strftime('%d/%m/%Y %H:%M:%S')} +_+_+_+ Линк существует {issue.issue_key} +_+_+_+")
            return True
        elif (self.confluence_viewpage.format(
                str(issue.confluence_id)) not in urls) and not self.get_confluence_page_id(
                title=self.confluence_title.format(issue.issue_key)):
            logger.info(
                f"{datetime.now().strftime('%d/%m/%Y %H:%M:%S')} +_+_+_+ Линк не существует {issue.issue_key} +_+_+_+")
            return False
        else:
            logger.info(
                f"{datetime.now().strftime('%d/%m/%Y %H:%M:%S')} +_+_+_+ Статья существует, линк тоже но по какой-то причине не отрабатывается провверкой {issue.issue_key} +_+_+_+")
            issue.confluence_id = self.get_confluence_page_id(title=self.confluence_title.format(issue.issue_key))
            issue.save()
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

    def save_issue(self, issue_key, issue_summary, release_name, issue_status):
        Issue.objects.create(issue_key=issue_key,
                             jira_url=''.join([self.JIRA_BASE_URL, "browse/", issue_key]),
                             issue_summary=issue_summary,
                             issue_status=issue_status,
                             release_name=release_name,
                             confluence_id=self.get_confluence_page_id(
                                 title=self.confluence_title.format(issue_key)))
