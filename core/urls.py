from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf.urls import patterns
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'core.views.home', name='core_home_page'),
    url(r'^test', 'core.views.test', name='core_test_page'),
    url(r'^login', 'core.views.view_login', name='core_login_page'),
)