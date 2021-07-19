import logging
from django.contrib import messages
from django.shortcuts import render, redirect
from django.views.generic import View

from monitor.atlassian_monitoring.atlassian_monitor import AtlassianMonitor
from monitor.models import Issue
# Create your views here.
from monitor.atlassian_monitoring.issue_processor import ReleaseProcessor

logger = logging.getLogger('django')


class MainPage(View):


    def get(self, *args, **kwargs):
        release_processor = ReleaseProcessor(self.request)
        current_releases = release_processor.get_feature_releases_info()
        issues_exists = Issue.objects.all().exists()
        context = {'releases': current_releases, 'has_issue': issues_exists}
        return render(self.request, 'main_page.html', context)

    def request_handler(self):
        release_processor = ReleaseProcessor(self.request)
        if self.request.POST.get('monitor'):
            release_processor.jira_monitoring()
            return

        if self.request.POST.get('release_name'):
            # Проверяем что все таски из релиза в статусе ready for release
            if release_processor.release_ready_for_report(self.request.POST.get('release_name')):
                # Перекладывваем таски относящиеся к релизу в иерапхию ГОД > РЕЛИЗ > ЗАДАЧИ
                release_processor.create_release_report()
            else:
                messages.warning(self.request, 'Не все задачи из релиза прошли тестирование')

        else:
            monitor = AtlassianMonitor(request=self.request)
            if monitor.issue_is_rc():
                logger.info('Задача пропущена т.к. тип задачи RC')
                return

            if monitor.issue_event == monitor.JIRA_ISSUE_UPDATED:
                monitor.check_and_update_issue()
                if monitor.issue_ready_for_qa():
                    monitor.create_report()
                    return

            elif monitor.issue_event == monitor.JIRA_ISSUE_CREATED:
                monitor.save_issue()
                logger.info('Create database entry for created issue')
                return

    def post(self, *args, **kwargs):
        self.request_handler()
        return redirect('/')

