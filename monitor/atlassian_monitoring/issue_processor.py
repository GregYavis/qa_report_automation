import json
import logging
import os
from datetime import datetime
from enum import Enum
from nested_lookup import nested_lookup
from atlassian import Confluence
from atlassian import Jira

from monitor.atlassian_monitoring.base import AtlassianConfig
from monitor.models import Issue

logging.basicConfig(filename='cron.log')
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
file = logging.FileHandler('cron.log')
file.setLevel(logging.INFO)
# formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logger.addHandler(file)





class ReleaseProcessor(AtlassianConfig):

    def __init__(self):
        super(ReleaseProcessor, self).__init__()

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
        return [e.value for e in self.issue_states if e not in
                [self.issue_states.RELEASED, self.issue_states.READY_FOR_QA]]

    def release_report(self, request):
        """
        Получаем имя страны, текущий год
        year_parent_id = id страницы с именем "Выпущенные релизы ГОД"
        В папке года создаем отчет по релизу имя которого получили из value кнопки
        Пример нового шаблона https://confluence.4slovo.ru/pages/viewpage.action?pageId=95485966
        release_parent_id = id созданной страницы релиза
        Все задачи относящиеся к данному релизу, переносим в папку релиза - меняется partner_id
        :return:
        """
        release_country = request.POST.get('release_name').split('.')[0]
        year = datetime.now().year
        print(year)
        print(self.confluence.get_page_by_title(space='AT', title=f'Выпущенные релизы {year}')['id'])
        # self.confluence.get_page_by_title(space="AT", title=confluence_title)
        return release_country

    # Проверяем таски уже занесенные в бд и имеющие шаблон отчета на факт смены статуса у задачи и обновляем его
    # Далее необходимо переделать под вебхук
    """
    def check_and_update_issues(self):
        issues = Issue.objects.all()
        for issue in issues:
            jira_issue_status = self.get_issue_status(issue.issue_key)
            logger.info(f'Check status- {issue.jira_url}.')
            # Вынести в update by status
            if issue.issue_status != jira_issue_status and jira_issue_status in self.possible_states():
                self.update_issue_status(issue_key=issue.issue_key, issue_status=jira_issue_status)
            # В противном случае считаем что задача вернулась в разработку
            elif issue.issue_status == jira_issue_status:
                pass
            else:
                self.update_issue_status(issue_key=issue.issue_key,
                                         issue_status=self.issue_states.IN_DEVELOPMENT.value)

            # Вынести в update by release_name
            jira_issue_release_name = self.get_release_name(issue.issue_key)
            if issue.release_name != jira_issue_release_name:
                self.update_issue_release_name(issue_key=issue.issue_key,
                                               release=jira_issue_release_name)

        # print(self.confluence.get_page_space(37127258))
        """

    """
    def jira_monitoring(self):
        data = self.jira.jql(self.QA_QUERY)
        for issue in data["issues"]:
            issue_key = issue['key']

            links = self.jira.get_issue_remote_links(issue['id'])
            # Условие для создания статьи с шаблоном отчета тестирования
            if not self.find_confluence_mentions(doc=links) and not self.issue_already_processed(issue_key):
                print('NOT')
                #print(issue_key)
                # Занести в SQLite
                logger.info(f'Create issue object in database for {issue_key}.')
                Issue.objects.create(issue_key=issue_key,
                                     issue_summary=self.get_issue_summary(issue_key),
                                     jira_url=self.jira.url + f"browse/{issue_key}",
                                     release_name=self.get_release_name(issue_key),
                                     issue_status=self.get_issue_status(issue_key=issue_key))
                                     """
    """
    def confluence_monitoring(self):
        # Плучаем данные из SQLite и для каждой производим проверку
        # Для каждой записи из SQLite проверяем есть ли к ней отчет
        issues = Issue.objects.all()
        # issue = Issue.objects.first()
        for issue in issues:
            confluence_title = f'{issue.issue_key}. Отчет о тестировании'
            if not self.confluence.page_exists(space="AT", title=confluence_title):
                issue_status = self.get_issue_status(issue.issue_key)
                # Создаем шаблон отчета
                logger.info(f'Create report template for {issue.issue_key} in Confluence.')
                #self.confluence.create_page(space='AT',
                #                            # title = 'f'{issue.issue_key}. Отчет о тестировании'',
                #                            title=confluence_title,
                #                            body=report_template(issue_key=issue.issue_key,
                #                                                 issue_url=issue.jira_url,
                #                                                 issue_status=issue_status,
                #                                                 issue_summary=issue.issue_summary),
                                            # parent_id=MUSORKA,
                #                            parent_id=37127275)
                confluence_id = self.confluence.get_page_by_title(space="AT", title=confluence_title)
                self.set_issue_confluence_id(issue_key=issue.issue_key, confluence_id=0)#confluence_id['id'])
                # добавляем в links_to страницу в кофлюенсе
            # Для тестирования во время разработки, проверяем на уже записанных в бд тасках что линка добавляется и апдейтится конф айди в бд
            else:
                confluence_id = self.confluence.get_page_by_title(space="AT", title=confluence_title)['id']
                self.set_issue_confluence_id(issue_key=issue.issue_key, confluence_id=confluence_id)
            #####################
            current_issue = Issue.objects.get(issue_key=issue.issue_key)
            links = self.jira.get_issue_remote_links(current_issue.issue_key)
            if not self.find_confluence_mentions(doc=links):
                print('ISSUE HAVE NO LINKS')
                #self.jira.create_or_update_issue_remote_links(issue_key=current_issue.issue_key,
                #                                              link_url=self.confluence_link(confluence_id),
                #                                              title=confluence_title)

            else:
                print("pass")
"""
