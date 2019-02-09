from django.conf.urls import patterns, include, url
from django.conf import settings
from django.views.generic import TemplateView
import django.views.defaults

from django.contrib import admin
admin.autodiscover()

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
                       url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
                       url(r'^admin/',     include(admin.site.urls)),
                       url(r'^/?$',        TemplateView.as_view(template_name='misc/homepage.html')),
                       url(r'^index.*/?$', TemplateView.as_view(template_name='misc/homepage.html')),
                       )

urlpatterns += patterns('django.views.defaults',
                        url(r'^errors/403/?$','permission_denied'), 
                        url(r'^errors/404/?$','page_not_found'),
                        url(r'^errors/500/?$','server_error'),
                        )

urlpatterns +=patterns('',
                       url(r'^css/',        include('css.urls')),
                       url(r'^javascript/', include('javascript.urls')),
                       url(r'^santaclara/', include('santaclara.urls')),
                       url(r'^base/',       include('base.urls')),
                       # url(r'^help/',       include('help.urls')),
                       url(r'^corpora/',    include('corpora.urls')),
                       # url(r'^dictionary/', include('dictionary.urls')),
                       url(r'^languages/',  include('languages.urls')),
                       # url(r'^morphology/', include('morphology.urls')),
                       )
