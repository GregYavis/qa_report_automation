import logging
from datetime import datetime
from nested_lookup import nested_lookup
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
                               issue.issue_status in self.in_qa_states())
        info = {release_name: {
            issue.issue_key: {'status': issue.issue_status, 'summary': issue.issue_summary, 'url': issue.jira_url}
            for issue in Issue.objects.filter(release_name=release_name)}
                for release_name in feature_releases}
        return info


    def in_qa_states(self):
        return [e.value for e in self.issue_states if e not in [self.issue_states.RELEASED,
                                                                self.issue_states.CLOSED,
                                                                self.issue_states.CLOSED_RU,
                                                                self.issue_states.FIXED,
                                                                self.issue_states.FIXED_RU,
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

    def release_ready_for_report(self, release_name: str):
        issues_in_release = Issue.objects.filter(release_name=release_name)
        ready_issues = Issue.objects.filter(release_name=release_name, issue_status__in=self.in_qa_states())
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
        if not self.confluence.page_exists(space='AT', title=release_title):
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
            issue.release_report = True
            issue.save()



