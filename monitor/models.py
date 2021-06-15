from django.db import models
from django.shortcuts import reverse


# Create your models here.

class Issue(models.Model):
    issue_key = models.CharField(max_length=56, unique=True)
    issue_url = models.CharField(max_length=512)
    create_ts = models.DateTimeField(auto_now_add=True)
    issue_released = models.BooleanField(default=0)
