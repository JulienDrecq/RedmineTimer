from django.db import models
from django.contrib.auth.models import User
from redmine_auth import settings
from datetime import datetime


class Issue(models.Model):
    user = models.ForeignKey(User)
    redmine_issue_id = models.BigIntegerField()
    name = models.CharField(max_length=256)
    project = models.CharField(max_length=256)
    date = models.DateField(auto_now_add=True)

    def __unicode__(self):
        return u"#%s - %s" % (self.redmine_issue_id, self.name)

    def __str__(self):
        return "#%s - %s" % (self.redmine_issue_id, self.name)

    def get_link_issue_on_redmine(self):
        return u"%s/issues/%s" % (settings.REDMINE_SERVER_URL, self.redmine_issue_id)


class TimeEntry(models.Model):
    user = models.ForeignKey(User)
    issue = models.ForeignKey(Issue)
    redmine_timentry_id = models.BigIntegerField()
    time = models.FloatField()
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(auto_now_add=False)
    comments = models.CharField(max_length=256)
