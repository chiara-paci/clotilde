from django.conf.urls import patterns, include, url
from django.conf import settings

from django.views.generic import DetailView,ListView

from corpora.models import Corpus,Text
from corpora.views import AlphaParserView,TextView

urlpatterns =patterns('',
                      ( r'^/?$',
                        ListView.as_view(queryset=Corpus.objects.order_by('name'),
                                         context_object_name="corpus_list")),
                      ( r'^corpus/(?P<pk>\d+)/?$',
                        DetailView.as_view(model=Corpus,context_object_name="corpus")),
                      ( r'^text/(?P<pk>\d+)/?$',
                        TextView.as_view(model=Text,context_object_name="text")),
                      ( r'^text/(?P<text_id>\d+)/alpha_parser/?$',
                        AlphaParserView.as_view()),
                      )

  # r'^text/(?P<pk>\d+)/alpha_parser/?$'
  # r'^text/(?P<pk>\d+)/alpha_token/?$'
  # r'^text/(?P<pk>\d+)/morphological_parser/?$'
  # r'^text/(?P<pk>\d+)/morphological_token/?$'
  # r'^text/(?P<pk>\d+)/syntax_parser/?$'
