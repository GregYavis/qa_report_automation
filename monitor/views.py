import ctypes
import json
import logging

from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View

import monitor
from monitor import models
from monitor.atlassian_monitoring.atlassian_monitor import AtlassianMonitor, FeatureReleases
from monitor.atlassian_monitoring.issue_processor import IssueProcessingBasics
from nested_lookup import nested_lookup
# Create your views here.
from monitor.models import Issue

logger = logging.getLogger('django')


class MainPage(View, AtlassianMonitor):
    issue_processor = FeatureReleases()

    def get(self, *args, **kwargs):
        current_releases = self.issue_processor.get_feature_releases_info()
        context = {'releases': current_releases}
        return render(self.request, 'main_page.html', context)

    def post(self, *args, **kwargs):

        if self.request.POST.get('monitor'):
            # launch monitor
            print(self.request.POST.get('monitor'))
        elif self.request.POST.get('release_name'):
            # launch monitor
            print(self.request.POST.get('release_name'))

        else:
            atl_monitor = AtlassianMonitor(request=self.request)
            if atl_monitor.issue_is_rc():
                return redirect('/')

            if atl_monitor.issue_event == atl_monitor.JIRA_ISSUE_UPDATED:
                try:
                    # get issue from DB
                    logger.info('Check issue for status/name or summary updates')
                    # update if issue updated
                    atl_monitor.check_and_update_issue()

                    if atl_monitor.issue_ready_for_qa():
                        atl_monitor.create_confluence_article()

                except models.Issue.DoesNotExist:
                    # if not get
                    atl_monitor.insert_issue_to_database(*atl_monitor.get_issue_data())
                    # Write to DB too cause we must process updated issues before release AT176 too/
                    logger.info('Create database entry for updated issue not writen in DB')
            elif atl_monitor.issue_event == atl_monitor.JIRA_ISSUE_CREATED:

                atl_monitor.insert_issue_to_database(*atl_monitor.get_issue_data())
                logger.info('Create database entry for created issue')


            # if Issue.objects.get(issue_key=issue_key):

            # print(nested_lookup(key='key', document=request_json['issue']))
            # print(nested_lookup(key='id', document=request_json['issue']))

            # print(self.request.POST.get('email'))
            # print(args, kwargs)
            # print(self.atlassian_monitor.all_release_tasks_ready(release_name=self.request.POST.get('release_name')))
            # print(self.request.POST.get('release_name'))
            # get that release tasks ready -> launch move_task
            # Process webhook data

        return redirect('/')


"""def report(request):
    #print(request.method)
        #release = Issue.objects.filter(release_name=request.POST)
    if request.method == "POST":
        print(request.POST.get('report_name'))
        return HttpResponse(status=200)"""
