from django.db import models
from django.contrib.auth.models import User


class RedmineUser(models.Model):
    user = models.OneToOneField(User)
    redmine_user_id = models.BigIntegerField(primary_key=True)
    username = models.CharField(max_length=256)
