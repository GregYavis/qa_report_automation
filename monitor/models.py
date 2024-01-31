from django.db import models
from django.shortcuts import reverse


# Create your models here.

class Release(models.Model):
    release_key = models.CharField(max_length=56, blank=True, null=True, unique=True, default='None')
    is_released = models.BooleanField(default=False)

    def __str__(self):
        return self.release_key


class Issue(models.Model):
    issue_key = models.CharField(max_length=56, unique=True)
    jira_url = models.CharField(max_length=512)
    confluence_id = models.IntegerField(blank=True, null=True)
    issue_summary = models.CharField(max_length=1024)
    create_ts = models.DateTimeField(auto_now_add=True)
    issue_status = models.CharField(max_length=90)
    release_name = models.ForeignKey('monitor.Release', on_delete=models.CASCADE)
    release_report = models.BooleanField(default=False)

    def __str__(self):
        return self.issue_key


