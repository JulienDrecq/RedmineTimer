from django.conf import settings

REDMINE_SERVER_URL = getattr(settings, 'REDMINE_SERVER_URL', 'https://localhost/')