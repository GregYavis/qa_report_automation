import logging
from datetime import datetime
from time import sleep

from monitor.atlassian_monitoring.base import AtlassianConfig
from monitor.models import Issue, Release
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



    def release_ready_for_report(self, release_name: str):
        issues_in_release = Issue.objects.filter(release_name=release_name)
        ready_issues = Issue.objects.filter(release_name=release_name, issue_status__in=self.ready_for_report_states())
        logger.info(f'{datetime.now().strftime("%d/%m/%Y %H:%M:%S")} Задачи в релизе {list(issues_in_release)}')
        logger.info(f'{datetime.now().strftime("%d/%m/%Y %H:%M:%S")} Обрабатываемые задачи {list(ready_issues)}')
        if list(issues_in_release) != list(ready_issues):
            logger.info(f'{datetime.now().strftime("%d/%m/%Y %H:%M:%S")} Задачи по которым не сходится список к отчету и фактический {set(issues_in_release).difference(set(ready_issues))}')
        return list(issues_in_release) == list(ready_issues)

    def monitor_issues_manual(self, release_name, first: bool):

        """
        При нажатии кнопки проверяем атрибуты задач на актуальность, на тот случай
        Если на момент обновления одного из атрибутов сервис был не доступен для вебхука,
        и при условии отличия актуальных и ранее сохраненных атрибутов обновляем их
        """
        # Что бы задачи не пролетали мимо бота в случае если перешли в тестирование во время когда он был не доступен
        if first:
            self.first_launch_get_issues()
        #
        # Найти все таски из релиза, если их нет в БД, добавить.
        issues = Issue.objects.filter(release_name=release_name)
        logger.info(
            f'{datetime.now().strftime("%d/%m/%Y %H:%M:%S")} Проверка актуальности атрибутов задач перед созданием отчета')
        for issue in issues:
            jira_issue_summary = self.issue_summary(issue.issue_key)
            jira_release_name = self.release_name(issue.issue_key)
            jira_issue_status = self.issue_status(issue.issue_key)
            confluence_id = self.get_confluence_page_id(title=self.confluence_title.format(issue.issue_key))
            if confluence_id is None:
                issue_conf_info = self.confluence.create_page(space='AT',
                                                              title=self.confluence_title.format(issue.issue_key),
                                                              body=issue_report_template(issue.issue_key),
                                                              parent_id=self.qa_reports_page_id)
                logger.info(f"{datetime.now().strftime('%d/%m/%Y %H:%M:%S')} ***** {issue_conf_info} *****")
                issue.confluence_id = self.get_confluence_page_id(
                    title=self.confluence_title.format(issue.issue_key))
                confluence_id = issue.confluence_id
                issue.save()
            # Проверить нет ли уже линка у задачи
            try:
                if not self.check_report_link_in_remote_links(issue=issue):
                    self.create_link(issue=issue)
            except Exception:
                logger.info(f'{datetime.now().strftime("%d/%m/%Y %H:%M:%S")} *_*_* запрос на проверку линков к задаче {issue} не возможен, задача удалена или скрыта')
                continue
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
        release_name = Release.objects.get(id=self.request.POST.get('release_name'))
        logger.info(f'{release_name}')
        country = str(release_name).split('.')[0]

        year_title = self.year_releases.format(datetime.now().year)
        if not self.confluence.page_exists(space="AT", title=year_title):
            self.confluence.create_page(space='AT', title=year_title, parent_id=self.qa_reports_page_id)
        year_id = self.get_confluence_page_id(title=self.year_releases.format(datetime.now().year))

        release_title = self.release_report_title.format(release_name)

        # Создаем шаблон релиза
        if not self.confluence.page_exists(space='AT', title=release_title):
            logger.info(
                f'{datetime.now().strftime("%d/%m/%Y %H:%M:%S")} Создание шаблона отчета для релиза {release_name}')
            self.confluence.create_page(space='AT',
                                        title=release_title,
                                        body=release_report_template(country=country),
                                        parent_id=year_id)
        release_name.is_released = True
        release_name.save()
        # Далее получаем таски релиза release_name
        release_issues = Issue.objects.filter(release_name=release_name)
        release_report_id = self.get_confluence_page_id(title=release_title)
        for issue in release_issues:
            logger.info(
                f'{datetime.now().strftime("%d/%m/%Y %H:%M:%S")} Перенос отчета задачи {issue} в родительскую папку {release_title} с id {release_report_id}')
            self.confluence.update_page(page_id=issue.confluence_id,
                                        title=self.confluence_title.format(issue.issue_key),
                                        parent_id=release_report_id)
            issue.release_report = True
            issue.save()

    def first_launch_get_issues(self):
        data = self.jira.jql(self.QA_QUERY)
        processed_releases = []
        for issue in data["issues"]:

            issue_key = issue['key']
            logger.info(f'{datetime.now().strftime("%d/%m/%Y %H:%M:%S")} {issue_key} proceed thru first_launch method.')
            try:
                # Для сборок не создаем таких же отчетов как для тасок
                if self.jira.issue_field_value(key=issue_key, field='issuetype')['name'] == 'RC':
                    continue
            except TypeError:
                pass

            if not self.confluence.page_exists(space='AT', title=self.confluence_title.format(issue_key)):
                self.create_template(issue_key)

            if not Issue.objects.filter(issue_key=issue_key):
                self.create_issue(issue_key=issue_key)

            issue = Issue.objects.get(issue_key=issue_key)
            # Проверяем есть ли у задачи прикрепленный линк с отчетом о тестировании, если нету, создаем.
            if not self.check_report_link_in_remote_links(issue=issue):
                logger.info(
                    f'{datetime.now().strftime("%d/%m/%Y %H:%M:%S")} Прикрепляем ссылку на отчет о тестировании задачи {issue_key}.')
                self.create_link(issue=issue)
            processed_releases.append(self.release_name(issue_key))
            processed_releases[:] = set(processed_releases)
        # Дополнительно подтягиваем данные о всех задачах по затронутым релизам
        for release in processed_releases:
            if release is not None:
                issues_by_release_name = self.jira.jql(self.ISSUES_BY_RELEASE.format(release))
                for _issue in issues_by_release_name["issues"]:
                    _issue_key = _issue['key']
                    try:
                        # Для сборок не создаем таких же отчетов как для тасок
                        if self.jira.issue_field_value(key=_issue_key, field='issuetype')['name'] == 'RC':
                            continue
                    except TypeError:
                        pass
                    if not Issue.objects.filter(issue_key=_issue_key):
                        self.create_issue(issue_key=_issue_key)
