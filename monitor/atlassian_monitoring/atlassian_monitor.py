import logging
import logging.handlers
import multiprocessing

from confluence_table_template import report_template
from .issue_processor import IssueProcessingBasics
from monitor.models import Issue

logging.basicConfig(filename='cron.log')
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
file = logging.FileHandler('cron.log')
file.setLevel(logging.INFO)
# formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logger.addHandler(file)
"""
python manage.py crontab add
python manage.py crontab run cc96dca57171b6521384fa538a69f69d
python manage.py crontab remove
"""

"""
Проверяем через апи джиры наличие задач реди фор куа
Проверяем их на наличие статьи-шаблона в конфе,
Если нет, заводим статью шаблон с нужным именем и таблицей
"""


class AtlassianMonitor(IssueProcessingBasics):
    def __init__(self):
        super(AtlassianMonitor, self).__init__()

    def jira_monitoring(self):
        data = self.jira.jql(self.QA_QUERY)
        for issue in data["issues"]:
            issue_key = issue['key']

            links = self.jira.get_issue_remote_links(issue['id'])
            # Условие для создания статьи с шаблоном отчета тестирования
            if not self.find_confluence_mentions(doc=links) and not self._issue_already_processed(issue_key):
                print('NOT')
                # Занести в SQLite
                logger.info(f'Create issue object in database for {issue_key}.')
                Issue.objects.create(issue_key=issue_key,
                                     issue_summary=self.get_issue_summary(issue_key),
                                     jira_url=self.jira.url + f"browse/{issue_key}",
                                     release_name=self.get_release_name(issue_key),
                                     issue_status=self._get_issue_status(issue_key=issue_key))

    def confluence_monitoring(self):
        # Плучаем данные из SQLite и для каждой производим проверку
        # Для каждой записи из SQLite проверяем есть ли к ней отчет
        issues = Issue.objects.all()
        # issue = Issue.objects.first()
        for issue in issues:
            confluence_title = f'{issue.issue_key}. Отчет о тестировании'
            if not self.confluence.page_exists(space="AT", title=confluence_title):
                issue_status = self._get_issue_status(issue.issue_key)
                # Создаем шаблон отчета
                logger.info(f'Create report template for {issue.issue_key} in Confluence.')
                self.confluence.create_page(space='AT',
                                            # title = 'f'{issue.issue_key}. Отчет о тестировании'',
                                            title=confluence_title,
                                            body=report_template(issue_key=issue.issue_key,
                                                                 issue_url=issue.jira_url,
                                                                 issue_status=issue_status,
                                                                 issue_summary=issue.issue_summary),
                                            # parent_id=MUSORKA,
                                            parent_id=37127275)
                confluence_id = self.confluence.get_page_by_title(space="AT", title=confluence_title)
                self.set_issue_confluence_id(issue_key=issue.issue_key, confluence_id=confluence_id['id'])
                # добавляем в links_to страницу в кофлюенсе
            # Для тестирования во время разработки, проверяем на уже записанных в бд тасках что линка добавляется и апдейтится конф айди в бд
            else:
                confluence_id = self.confluence.get_page_by_title(space="AT", title=confluence_title)['id']
                self.set_issue_confluence_id(issue_key=issue.issue_key, confluence_id=confluence_id)
            #####################
            current_issue = Issue.objects.get(issue_key=issue.issue_key)
            links = self.jira.get_issue_remote_links(current_issue.issue_key)
            if not self.find_confluence_mentions(doc=links):
                self.jira.create_or_update_issue_remote_links(issue_key=current_issue.issue_key,
                                                              link_url=self.confluence_link(confluence_id),
                                                              title=confluence_title)

            else:
                print("pass")

    def confluence_link(self, confluence_id):
        return ''.join([self.confluence_viewpage, str(confluence_id)])

    # Проверяем таски уже занесенные в бд и имеющие шаблон отчета на факт смены статуса у задачи и обновляем его
    def check_and_update_issues(self):
        issues = Issue.objects.all()
        for issue in issues:
            jira_issue_status = self._get_issue_status(issue.issue_key)
            logger.info(f'Check status- {issue.jira_url}.')
            # Вынести в update by status
            if issue.issue_status != jira_issue_status and jira_issue_status in self._possible_states():
                self._update_issue_status(issue_key=issue.issue_key, issue_status=jira_issue_status)
            # В противном случае считаем что задача вернулась в разработку
            elif issue.issue_status == jira_issue_status:
                pass
            else:
                self._update_issue_status(issue_key=issue.issue_key,
                                          issue_status=self.issue_states.IN_DEVELOPMENT.value)

            # Вынести в update by release_name
            jira_issue_release_name = self.get_release_name(issue.issue_key)
            if issue.release_name != jira_issue_release_name:
                self.update_issue_release_name(issue_key=issue.issue_key,
                                               release=jira_issue_release_name)

        # print(self.confluence.get_page_space(37127258))

    # Сейчас используется для тестирования в кроне, при переходе на вебхук - убрать
    def get_active_releases(self):
        """
        Отследить последний релиз
        # Задача входящая в следующий релиз определяется по следующей логике
            выбираем из бд все задачи с  issue_status = 5 ,
        Для каждой задчи релиза отследить её текущий статус
        Если у всех заздач статус ready for release or released to production -
        Проверяем есть ли папка с текущим годом
        Если нет - создаем.
        В этой папке проверяем есть ли файл с текущим релизом
        Если нет - создать и заполнить таблицами отчета по регрессу.
        Переложить задачи в Папку (Год > Релиз > Отчеты по задачам входящим в релиз)
        :return:
        """
        # Получаем первую таску со статусуом RELEASED не имеющую отчета релиза,
        # следовательно её номер релиза - номер релиза для которого необходимо создать
        # папку в папке года и переложить в неё отчет по таскам из конфлюенса
        #                                                           # Заменить на RELEASED
        released_issues = Issue.objects.filter(issue_status=self.issue_states.READY_FOR_QA.value, release_report=False)
        current_releases = set(release.release_name for release in released_issues)
        logger.info(current_releases)
        # if released_issues.exists():
        # for issue in released_issues:
        #    issue_release_name = self.get_release_name(issue_key=str(issue.issue_key))
        #    logger.info(issue_release_name)

        # if released_issues:

    def all_release_tasks_ready(self, release_name):
        # get current state of tasks by
        # self.check_and_update_issues()
        ready_tasks = Issue.objects.filter(release_name=release_name,
                                           issue_status=self.issue_states.READY_FOR_RELEASE.value)
        all_release_tasks = Issue.objects.filter(release_name=release_name)
        return len(ready_tasks) == len(all_release_tasks)

    def move_page(self):
        #page_id = self.confluence.get_page_by_title()
        # need get current year, release that task relate to,
        release_name = 'ru.6.3.25'
        _release_id = self.confluence.get_page_by_title(space="AT", title=f'Релиз {release_name} Отчет о тестировании')
        print(_release_id)
        updated_issue = Issue.objects.get(issue_key='SLOV-6950')
        page_id = updated_issue.confluence_id
        confluence_title = f'{updated_issue.issue_key}. Отчет о тестировании'
        self.confluence.update_page(page_id=page_id, title=confluence_title, parent_id=_release_id,)



    # a.confluence_monitoring("SLOV-6936")
