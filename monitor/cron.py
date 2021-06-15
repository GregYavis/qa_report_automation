import json
import os
import logging
from atlassian import Confluence
from atlassian import Jira
from monitor.models import Issue

logging.basicConfig(filename='cron.log')

"""
python manage.py crontab add
python manage.py crontab run cc96dca57171b6521384fa538a69f69d
python manage.py crontab remove
"""

"""
Проверяем через апи жиры наличие задач реди фор куа
Проверяем их на наличие статьи-шаблона в конфе,
Если нет, заводим статью шаблон с нужным именем и таблицей
"""
class AtlassianMonitor:
    ROOT_PATH = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    CONFIG_PATH = os.path.join(ROOT_PATH, 'config.json')
    # Шаблон запроса задач в статусе Ready for QA
    READY_FOR_QA_QUERY = 'project = 4Slovo AND status = "Ready for QA" ORDER BY priority DESC'
    def __init__(self):
        self.config = json.load(open(self.CONFIG_PATH))
        self.jira = Jira(url=self.config["JIRA_URL"],
                         username=self.config["USERNAME"],
                         password=self.config["PASSWORD"])
        self.confluence = Confluence(url=self.config["CONFLUENCE_URL"],
                                     username=self.config["USERNAME"],
                                     password=self.config["PASSWORD"])

        # self.confluence = Confluence()
        self.tasks = []

    @staticmethod
    def __confluence_mentions_in_links(links):
        return [link for link in links if 'name' in link['application'] and 'confluence' in link['object']['url']]

    @staticmethod
    def __issue_already_processed(issue_key):
        return Issue.objects.filter(issue_key=issue_key)

    def jira_ready_for_qa_monitoring(self):
        data = self.jira.jql(self.READY_FOR_QA_QUERY)
        for issue in data["issues"]:
            links = self.jira.get_issue_remote_links(issue['id'])
            # Условие для создания статьи с шаблоном для отчета тестирования
            if not any(self.__confluence_mentions_in_links(links)) and not self.__issue_already_processed(issue['key']):
                # Занести в SQLite
                Issue.objects.create(issue_key=issue['key'], issue_url=self.jira.url + f"browse/{issue['key']}")
                # Создать шаблон отчета в конфлюенсе
                print(issue['key'])
                self.tasks.append(issue['key'])
        return self.tasks

    def confluence_monitoring(self, issue_key):
        # Плучаем данные из SQLite и для каждой производим проверку
        # Для каждой записи из SQLite проверяем есть ли к ней отчет
        issues = Issue.objects.all()

        if not self.confluence.page_exists(space="AT", title=f'{issue_key}. Отчет о тестировании'):
            print('YEA')
        return issues
        """
        Для каждой задачи в статусе READY
        проверяем нет ли для неё отчета в конфлю,
        если нету создаем,
        """
        #print(self.confluence.get_page_space(37127258))

def do():
    atl = AtlassianMonitor()
    issue = atl.jira_ready_for_qa_monitoring()
    processed = atl.confluence_monitoring("SLOV-6936")
    with open('/home/greg/PycharmProjects/qa_report/sample.txt', 'a') as f:
        f.write(f'{issue}\n')
        for i in processed:
            f.write(f'{i.issue_url}\n')
        f.close()


if __name__ == '__main__':
    a = AtlassianMonitor()
    a.jira_ready_for_qa_monitoring()
    #a.confluence_monitoring("SLOV-6936")