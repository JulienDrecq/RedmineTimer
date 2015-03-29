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
    url(r'^timer/(?P<timer_id>\d+)$', 'core.views.view_timer', name='core_timer'),
    url(r'^timer/(?P<timer_id>\d+)/download_time_entries$', 'core.views.download_time_entries',
        name='core_download_time_entries'),
    url(r'^timer/(?P<timer_id>\d+)/upload_time_entries$', 'core.views.upload_time_entries',
        name='core_upload_time_entries'),
    url(r'^timer/(?P<timer_id>\d+)/refresh_issue', 'core.views.refresh_issue',
        name='core_refresh_issue'),
    url(r'^from/(?P<start_date>\d{4}-\d{2}-\d{2})/to/(?P<end_date>\d{4}-\d{2}-\d{2})$',
        'core.views.from_to_time_entries', name='core_from_to_time_entries'),
    url(r'^filter_date', 'core.views.filter_date', name='core_filter_date'),
    url(r'^timer/(?P<timer_id>\d+)/entry/(?P<entry_id>\d+)/edit', 'core.views.edit_entry', name='core_edit_entry'),
    url(r'^timer/(?P<timer_id>\d+)/entry/(?P<entry_id>\d+)/delete', 'core.views.delete_entry', name='core_delete_entry'),
    url(r'^timer/(?P<timer_id>\d+)/entry/(?P<entry_id>\d+)/upload', 'core.views.upload_entry', name='core_upload_entry'),
)