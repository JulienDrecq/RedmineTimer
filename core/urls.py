from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf.urls import patterns
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'core.views.view_home', name='core_home'),
    url(r'^login', 'core.views.view_login', name='core_login'),
    url(r'^logout', 'core.views.view_logout', name='core_logout'),
    url(r'^new_timer', 'core.views.new_timer', name='core_new_timer'),
    url(r'^start_new_timer', 'core.views.start_new_timer', name='core_start_new_timer'),
    url(r'^issue/(?P<issue_id>\d+)$', 'core.views.view_issue', name='core_issue'),
    url(r'^issue/(?P<issue_id>\d+)/synchronize_time_entries$', 'core.views.synchronize_time_entries',
        name='core_synchronize_time_entries'),
)