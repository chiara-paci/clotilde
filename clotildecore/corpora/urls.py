from django.conf.urls import patterns, include, url
from django.conf import settings

from django.views.generic import DetailView,ListView

from . import models

urlpatterns =[
    url( r'^/corpus/?$',ListView.as_view(queryset=Corpus.objects.order_by('name')),name="corpus_list" ),
    url( r'^/corpus/(?P<pk>\d+)/?$',DetailView.as_view(model=Corpus),name="corpus_detail"),
    url( r'^/text/(?P<pk>\d+)/?$',TextView.as_view(model=Text,context_object_name="text")),
    url( r'^/text/(?P<text_id>\d+)/alpha_parser/?$',AlphaParserView.as_view()),
]

  # r'^text/(?P<pk>\d+)/alpha_parser/?$'
  # r'^text/(?P<pk>\d+)/alpha_token/?$'
  # r'^text/(?P<pk>\d+)/morphological_parser/?$'
  # r'^text/(?P<pk>\d+)/morphological_token/?$'
  # r'^text/(?P<pk>\d+)/syntax_parser/?$'
