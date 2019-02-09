from django.conf.urls import patterns, include, url
from django.conf import settings

from django.views.generic import DetailView,ListView

from . import models

urlpatterns =[
    url( r'^/caseset/(?P<pk>\d+)/?$',DetailView.as_view(model=models.CaseSet),name="caseset_detail"),
    url( r'^/casepair/(?P<pk>\d+)/?$',DetailView.as_view(model=models.CasePair),name="casepair_detail"),
    url( r'^/language/?$',ListView.as_view(queryset=Language.objects.order_by('name')),name="language_list"),
    url( r'^/language/(?P<pk>\d+)/?$',DetailView.as_view(model.Language),name="language_detail"),
]

