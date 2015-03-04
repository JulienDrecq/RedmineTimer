from django.contrib.auth.models import User
from redmine_auth.models import RedmineUser
from redmine_auth.settings import *
from redmine import Redmine
from redmine.exceptions import AuthError
import logging
logger = logging.getLogger(__name__)


class RedmineBackend(object):

    def authenticate(self, username=None, password=None):
        user = None
        try:
            redmine_user = Redmine(REDMINE_SERVER_URL, username=username, password=password).auth()
            try:
                django_redmine_user = RedmineUser.objects.get(redmine_user_id=redmine_user.id)
                if django_redmine_user.username != username:
                    django_redmine_user.username = username
                    django_redmine_user.save()
                user = django_redmine_user.user
            except RedmineUser.DoesNotExist:
                user, created = User.objects.get_or_create(username=username)
                user.save()
                django_redmine_user = RedmineUser(user=user, username=username, redmine_user_id=redmine_user.id)
                django_redmine_user.save()
        except AuthError:
            logger.error('Exception with Redmine authentificate. Username or password invalid.')
            return None
        return user

    def get_user(self, user_id):
        try:
            return RedmineUser.objects.get(user=user_id).user
        except RedmineUser.DoesNotExist:
            logger.error('No Redmine user identified with id : %s' % user_id)
            return None