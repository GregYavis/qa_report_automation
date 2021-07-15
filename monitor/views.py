import logging
from django.contrib import messages
from django.shortcuts import render, redirect
from django.views.generic import View

from monitor.atlassian_monitoring.atlassian_monitor import AtlassianMonitor

# Create your views here.
from monitor.atlassian_monitoring.issue_processor import ReleaseProcessor

logger = logging.getLogger('django')


class MainPage(View):


    def get(self, *args, **kwargs):
        release_processor = ReleaseProcessor(self.request)
        current_releases = release_processor.get_feature_releases_info()
        context = {'releases': current_releases}
        return render(self.request, 'main_page.html', context)

    def request_handler(self):
        release_processor = ReleaseProcessor(self.request)
        #if self.request.POST.get('monitor'):
        #    # launch monitor
        #    #print(self.request.POST)
        #    print(self.request.body.decode('utf-8'), type(self.request.body.decode('utf-8')))
        #    #print(self.request.POST.get('monitor'))
        if self.request.POST.get('release_name'):
            # launch monitor
            # Перекладывваем таски относящиеся к релизу в ГОД (parent id) > РЕЛИЗ (parent id) (шаблонг отчета) > ТАСКИ
            if release_processor.release_ready_for_report(self.request.POST.get('release_name')):
                release_processor.create_release_report()
            else:
                messages.warning(self.request, 'Не все задачи из релиза прошли тестирование')


        else:
            monitor = AtlassianMonitor(request=self.request)
            if monitor.issue_is_rc():
                logger.info('Задача пропущена т.к. тип задачи RC')
                # Если RC готова к релизу, создать шаблон для отчета об исследовательском тестировании
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

