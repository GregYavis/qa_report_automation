import logging
from datetime import datetime

from monitor.atlassian_monitoring.base import AtlassianConfig
from monitor.models import Issue
from confluence_table_template import release_report_template, issue_report_template

logging.basicConfig(filename='cron.log')
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
file = logging.FileHandler('cron.log')
file.setLevel(logging.INFO)
logger.addHandler(file)


class ReleaseProcessor(AtlassianConfig):

    def __init__(self, request):
        super(ReleaseProcessor, self).__init__()
        self.year_releases = 'Выпущенные релизы {}'
        self.release_report_title = 'Релиз {} Отчет о тестировании'

        self.request = request

    @staticmethod
    def issues_to_release():
        issues_to_nearest_releases = Issue.objects.filter(confluence_id__isnull=False,
                                                          release_report=False,
                                                          release_name__isnull=False)
        #print([issue.release_name for issue in issues_to_nearest_releases])
        return [issue.release_name for issue in issues_to_nearest_releases]

    def get_feature_releases_info(self):
        issues_to_release = Issue.objects.filter(confluence_id__isnull=False,
                                                          release_report=False,
                                                          release_name__isnull=False)
        feature_releases = set(issue.release_name for issue in issues_to_release if
                               issue.issue_status in self.qa_states())
        info = {release_name: {
            issue.issue_key: {'status': issue.issue_status,
                              'summary': issue.issue_summary,
                              'url': issue.jira_url}
            for issue in Issue.objects.filter(release_name=release_name)}
                for release_name in feature_releases}
        return info


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
                                                                self.issue_states.IN_PROGRESS,
                                                                self.issue_states.IN_QA]]

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
                                                                self.issue_states.IN_QA]]

    def release_ready_for_report(self, release_name: str):
        issues_in_release = Issue.objects.filter(release_name=release_name)
        logger.info(list(issues_in_release))
        ready_issues = Issue.objects.filter(release_name=release_name, issue_status__in=self.ready_for_report_states())
        logger.info(list(ready_issues))
        return list(issues_in_release) == list(ready_issues)

    def monitor_issues_manual(self, release_name):
        """
        При нажатии кнопки проверяем атрибуты задач на актуальность, на тот случай
        Если на момент обновления одного из атрибутов сервис был не доступен для вебхука,
        и при условии отличия актуальных и ранее сохраненных атрибутов обновляем их
        """
        issues = Issue.objects.filter(release_name=release_name)

        logger.info('Проверка актуальности атрибутов задач перед созданием отчета')
        for issue in issues:

            jira_issue_summary = self.issue_summary(issue.issue_key)
            jira_release_name = self.release_name(issue.issue_key)
            jira_issue_status = self.issue_status(issue.issue_key)
            confluence_id = self.get_confluence_page_id(title=self.confluence_title.format(issue.issue_key))
            if not self.confluence.page_exists(space='AT', title=self.confluence_title.format(issue.issue_key)):
                self.confluence.create_page(space='AT',
                                            title=self.confluence_title.format(issue.issue_key),
                                            body=issue_report_template(issue.issue_key),
                                            parent_id=self.qa_reports_page_id)
                issue.confluence_id = self.get_confluence_page_id(title=self.confluence_title.format(issue.issue_key))
                issue.save()
                self.create_link(issue=issue)
            if jira_issue_summary != issue.issue_summary or \
                    jira_release_name != issue.release_name or \
                    jira_issue_status != issue.issue_status or \
                    confluence_id != issue.confluence_id:
                self.update_issue(issue_key=issue.issue_key,
                                  issue_summary=jira_issue_summary,
                                  issue_status=jira_issue_status,
                                  release_name=jira_release_name,
                                  confluence_id=confluence_id)
        return


    def create_release_report(self):
        """
        year_parent_id = id страницы с именем "Выпущенные релизы ГОД"
        В папке года создаем отчет по релизу имя которого получили из value кнопки
        Пример нового шаблона https://confluence.4slovo.ru/pages/viewpage.action?pageId=95485966
        release_parent_id = id созданной страницы релиза
        Все задачи относящиеся к данному релизу, переносим в папку релиза - меняется partner_id
        """
        release_name = self.request.POST.get('release_name')
        logger.info(f'{release_name}')
        country = release_name.split('.')[0]
        year_title = self.year_releases.format(datetime.now().year)
        if not self.confluence.page_exists(space="AT", title=year_title):
            self.confluence.create_page(space='AT', title=year_title, parent_id=self.qa_reports_page_id)
        year_id = self.get_confluence_page_id(title=self.year_releases.format(datetime.now().year))

        release_title = self.release_report_title.format(release_name)

        # Создаем шаблон релиза
        if not self.confluence.page_exists(space='AT', title=release_title):
            logger.info(f'Создание шаблона отчета для релиза {release_name}')
            self.confluence.create_page(space='AT',
                                        title=release_title,
                                        body=release_report_template(country=country),
                                        parent_id=year_id)

        # Далее получаем таски релиза release_name
        release_issues = Issue.objects.filter(release_name=release_name)
        release_report_id = self.get_confluence_page_id(title=release_title)
        for issue in release_issues:
            logger.info(f'Перенос отчета задачи {issue} в родительскую папку {release_title} с id {release_report_id}')
            self.confluence.update_page(page_id=issue.confluence_id,
                                        title=self.confluence_title.format(issue.issue_key),
                                        parent_id=release_report_id)
            issue.release_report = True
            issue.save()



    def first_launch_get_issues(self):
        data = self.jira.jql(self.QA_QUERY)
        for issue in data["issues"]:

            issue_key = issue['key']
            logger.info(f'{issue_key}.')
            try:
                # Для сборок не создаем таких же отчетов как для тасок
                if self.jira.issue_field_value(key=issue_key, field='issuetype')['name'] == 'RC':
                    continue
            except TypeError:
                pass

            if not self.confluence.page_exists(space='AT', title=self.confluence_title.format(issue_key)):
                # self.confluence_page(title=self.confluence_title.format(issue_key)):
                logger.info(f'Создание шаблона отчета для задачи {issue_key}.')
                self.confluence.create_page(space='AT',
                                            title=self.confluence_title.format(issue_key),
                                            body=issue_report_template(issue_key),
                                            parent_id=self.qa_reports_page_id)


            if not Issue.objects.filter(issue_key=issue_key):
                logger.info(f'Запись в БД {issue_key}.')
                self.save_issue(issue_key=issue_key,
                                issue_summary=self.issue_summary(issue_key),
                                release_name=self.release_name(issue_key),
                                issue_status=self.issue_status(issue_key))


            issue = Issue.objects.get(issue_key=issue_key)
            # Проверяем есть ли у задачи прикрепленный линк с отчетом о тестировании, если нету, создаем.
            if not self.check_report_link_in_remote_links(issue=issue):
                logger.info(f'Прикрепляем ссылку на отчет о тестировании задачи {issue_key}.')
                self.create_link(issue=issue)