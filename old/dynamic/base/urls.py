from django.conf.urls import patterns, include, url
from django.conf import settings

from django.views.generic import DetailView,ListView

from base.models import CaseSet

urlpatterns =patterns('',
                      ( r'^case-set/(?P<pk>\d+)/?$',
                        DetailView.as_view(model=CaseSet,context_object_name="caseset")),
                      )
