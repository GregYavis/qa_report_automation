from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.generic import View

from monitor.atlassian_monitoring.atlassian_monitor import AtlassianMonitor
from monitor.atlassian_monitoring.issue_processor import IssueProcessingBasics

# Create your views here.
from monitor.models import Issue


class MainPage(View):
    issue_processor = IssueProcessingBasics()
    atlassian_monitor = AtlassianMonitor()

    def get(self, *args, **kwargs):
        atl = AtlassianMonitor()
        atl.jira_monitoring()
        current_releases = self.issue_processor.get_current_releases_info()
        context = {'releases': current_releases}
        return render(self.request, 'main_page.html', context)

    def post(self, *args, **kwargs):
        print(self.request.POST)
        print(self.request.POST.get('email'))
        #print(args, kwargs)
        #print(self.atlassian_monitor.all_release_tasks_ready(release_name=self.request.POST.get('release_name')))
        print(self.request.POST.get('release_name'))
        # get that release tasks ready -> launch move_task
        # Process webhook data
        return redirect('/')

    """
    реализовать перекладывание отчетов
    Далее необходимо созвониться с ДИ и обсудить создание репозитория для проекта, а так же создание вебхука в jira
    """
"""def report(request):
    #print(request.method)
        #release = Issue.objects.filter(release_name=request.POST)
    if request.method == "POST":
        print(request.POST.get('report_name'))
        return HttpResponse(status=200)"""
