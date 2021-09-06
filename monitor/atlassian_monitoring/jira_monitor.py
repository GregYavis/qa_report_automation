import logging

from confluence_table_template import issue_report_template
from monitor.models import Issue
from monitor.atlassian_monitoring.base import AtlassianConfig

logging.basicConfig(filename='cron.log')
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
file = logging.FileHandler('cron.log')
file.setLevel(logging.INFO)
logger.addHandler(file)

class Monitor(AtlassianConfig):

    def __init__(self):
        super().__init__()

    # Обрабатываем текущие таски в статусах 'Ready for QA' 'Passed QA' 'In regression test' 'Ready for release'
    def jira_monitoring(self):
        data = self.jira.jql(self.QA_QUERY)
        for issue in data["issues"]:

            issue_key = issue['key']
            print(issue_key)
            try:
                # Для сборок не создаем таких же отчетов как для тасок
                if self.jira.issue_field_value(key=issue_key, field='issuetype')['name'] == 'RC':
                    continue
            except TypeError:
                pass
            links = self.jira.get_issue_remote_links(issue['id'])
            confluence_id = self.issue_confluence_id(links)
            if confluence_id is None and not self.confluence.page_exists(space='AT', title=self.confluence_title.format(issue_key)):
                #self.confluence_page(title=self.confluence_title.format(issue_key)):
                logger.info(f'Создание шаблона отчета для задачи {issue_key}.')
                self.confluence.create_page(space='AT',
                                            title=self.confluence_title.format(issue_key),
                                            body=issue_report_template(issue_key),
                                            parent_id=self.qa_reports_page_id)
            confluence_id = self.confluence_page(self.confluence_title.format(issue_key))['id']
            logger.info(f'Запись в БД {issue_key}.')
            if not Issue.objects.filter(issue_key=issue_key):
                Issue.objects.create(issue_key=issue_key,
                                     issue_summary=self.issue_summary(issue_key),
                                     jira_url=''.join([self.jira.url, f"browse/{issue_key}"]),
                                     release_name=self.release_name(issue_key),
                                     issue_status=self.issue_status(issue_key=issue_key),
                                     confluence_id=confluence_id)

            issue = Issue.objects.get(issue_key=issue_key)
            if not self.confluence_page(title=self.confluence_title.format(issue_key)):
                # Создать линку на созданную статью к задаче в jira
                if not confluence_id:
                    self.create_link(issue=issue)