from django.db import models
from django.shortcuts import reverse


# Create your models here.

class Issue(models.Model):
    STATES = (
        ('Ready for QA', 'Ready for QA'),
        ('Passed QA', 'Passed QA'),
        ('In regression test', 'In regression test'),
        ('Ready for release', 'Ready for release'),
        ('Released to production', 'Released to production')
    )
    issue_key = models.CharField(max_length=56, unique=True)
    jira_url = models.CharField(max_length=512)
    confluence_id = models.IntegerField(blank=True, null=True)
    issue_summary = models.CharField(max_length=1024)
    create_ts = models.DateTimeField(auto_now_add=True)
    issue_status = models.CharField(choices=STATES, max_length=30)
    release_name = models.CharField(max_length=56)
    release_report = models.BooleanField(default=False)
