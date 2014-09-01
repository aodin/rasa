# -*- coding: utf-8 -*
from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',
    # Examples:
    url(r'^$', '{{ project_name }}.views.hello_world', name='hello_world'),
    # url(r'^{{ project_name }}/', include('{{ project_name }}.foo.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^staff/', include(admin.site.urls)),
)
