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

    def get_feature_releases_info(self):
        issues_to_release = Issue.objects.filter(confluence_id__isnull=False,
                                                 release_report=False,
                                                 release_name__isnull=False)
        feature_releases = set(issue.release_name for issue in issues_to_release if
                               issue.issue_status in self._release_states())
        info = {release_name: {
            issue.issue_key: {'status': issue.issue_status, 'summary': issue.issue_summary, 'url': issue.jira_url}
            for issue in Issue.objects.filter(release_name=release_name)}
                for release_name in feature_releases}
        return info

    def _release_states(self):
        return [e.value for e in self.issue_states if e not in [self.issue_states.READY_FOR_QA]]

    def release_ready_for_report(self, release_name: str):
        issues_in_release = Issue.objects.filter(release_name=release_name)
        ready_issues = Issue.objects.filter(release_name=release_name, issue_status=self.issue_states.RELEASED.value)
        return list(issues_in_release) == list(ready_issues)


    def create_release_report(self):
        """
        year_parent_id = id страницы с именем "Выпущенные релизы ГОД"
        В папке года создаем отчет по релизу имя которого получили из value кнопки
        Пример нового шаблона https://confluence.4slovo.ru/pages/viewpage.action?pageId=95485966
        release_parent_id = id созданной страницы релиза
        Все задачи относящиеся к данному релизу, переносим в папку релиза - меняется partner_id
        """
        release_name = self.request.POST.get('release_name')
        country = self.request.POST.get('release_name').split('.')[0]
        year_id = self.confluence_page(title=self.year_releases.format(datetime.now().year))['id']
        release_title = self.release_report_title.format(release_name)
        # Создаем шаблон релиза
        self.confluence.create_page(space='AT',
                                    title=release_title,
                                    body=release_report_template(country=country),
                                    parent_id=year_id)
        # Далее получаем таски релиза release_name
        release_issues = Issue.objects.filter(release_name=release_name)

        release_report_id = self.confluence_page(title=release_title)['id']
        for issue in release_issues:
            self.confluence.update_page(page_id=issue.confluence_id,
                                        title=self.confluence_title.format(issue.issue_key),
                                        parent_id=release_report_id)


    def get_release_name(self, issue_key):
        release_name = self.jira.issue_field_value(issue_key, 'fixVersions')
        if release_name:
            return release_name[0]['name']
        else:
            return None

    def get_issue_summary(self, issue_key):
        return self.jira.issue_field_value(key=issue_key, field='summary')

    def get_issue_status(self, issue_key):
        return self.jira.issue_field_value(issue_key, 'status')['name']

    def issue_confluence_id(self, links):
        try:
            return self.confluence_mentions_in_links(links)[0]['object']['url'].split('=')[1]
        except IndexError:
            return None

    def confluence_page(self, title):
        return self.confluence.get_page_by_title(space='AT', title=title)

    def create_link(self, issue):
        new_article_confluence_id = self.confluence_page(title=self.confluence_title.format(issue.issue_key))['id']
        self.jira.create_or_update_issue_remote_links(issue_key=issue.issue_key,
                                                      link_url=''.join(
                                                          [self.confluence_viewpage, str(new_article_confluence_id)]),
                                                      title=self.confluence_title.format(issue.issue_key))

    # Обрабатываем текущие таски в статусах 'Ready for QA' 'Passed QA' 'In regression test' 'Ready for release'
    def jira_monitoring(self):
        data = self.jira.jql(self.QA_QUERY)
        for issue in data["issues"]:

            issue_key = issue['key']
            try:
                # Для сборок не создаем таких же отчетов как для тасок
                if self.jira.issue_field_value(key=issue_key, field='issuetype')['name'] == 'RC':
                    continue
            except TypeError:
                pass
            links = self.jira.get_issue_remote_links(issue['id'])
            confluence_id = self.issue_confluence_id(links)
            if confluence_id is None:
                confluence_id = self.confluence_page(self.confluence_title.format(issue_key))['id']
            logger.info(f'Запись в БД {issue_key}.')
            Issue.objects.create(issue_key=issue_key,
                                 issue_summary=self.get_issue_summary(issue_key),
                                 jira_url=''.join([self.jira.url, f"browse/{issue_key}"]),
                                 release_name=self.get_release_name(issue_key),
                                 issue_status=self.get_issue_status(issue_key=issue_key),
                                 confluence_id=confluence_id)

            issue = Issue.objects.get(issue_key=issue_key)

            if not self.confluence_page(title=self.confluence_title.format(issue_key)):
                logger.info(f'Создание шаблона отчета для задачи {issue_key}.')
                self.confluence.create_page(space='AT',
                                            title=self.confluence_title.format(issue_key),
                                            body=issue_report_template(issue_key),
                                            parent_id=self.qa_reports_page_id)
                # Создать линку на созданную статью к задаче в jira
                if not confluence_id:
                    self.create_link(issue=issue)
