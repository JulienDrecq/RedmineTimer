from django.db import models
from django.contrib.auth.models import User
from redmine_auth import settings


class Timer(models.Model):
    user = models.ForeignKey(User)
    redmine_issue_id = models.BigIntegerField()
    name = models.CharField(max_length=256)
    project = models.CharField(max_length=256)

    def __unicode__(self):
        return u"#%s - %s" % (self.redmine_issue_id, self.name)

    def __str__(self):
        return "%s - %s" % (self.redmine_issue_id, self.name)

    def get_link_issue_on_redmine(self):
        return u"%s/issues/%s" % (settings.REDMINE_SERVER_URL, self.redmine_issue_id)

    def get_time_total(self):
        time_total = 0
        for entry in self.timeentry_set.all():
            time_total += entry.time
        return time_total


class TimeEntry(models.Model):
    user = models.ForeignKey(User)
    timer = models.ForeignKey(Timer)
    redmine_timentry_id = models.BigIntegerField()
    time = models.FloatField()
    date = models.DateField()
    start_date = models.DateTimeField(auto_now_add=False, null=True)
    end_date = models.DateTimeField(auto_now_add=False, null=True)
    comments = models.CharField(max_length=256)
