from django.conf.urls import include, url
from django.conf import settings

from django.views.generic import DetailView,ListView

from . import models,views

urlpatterns =[
    url( r'^$',ListView.as_view(queryset=models.Corpus.objects.order_by('name')),name="corpus_list" ),
    url( r'^corpus/(?P<pk>\d+)/?$',DetailView.as_view(model=models.Corpus),name="corpus_detail"),
    url( r'^text/(?P<pk>\d+)/?$',views.TextView.as_view(),name="text_detail"),
    url( r'^text/(?P<pk>\d+)/alpha_parser/?$',views.TextAlphaParserView.as_view(),name="text_alpha_parser"),
    url( r'^text/(?P<pk>\d+)/alpha_token/?$',views.TextAlphaTokenView.as_view(),name="text_alpha_token"),
    url( r'^text/(?P<pk>\d+)/morphological_parser/?$',views.TextMorphologicalParserView.as_view(),name="text_morphological_parser"),
    url( r'^text/(?P<pk>\d+)/morphological_token/?$',views.TextMorphologicalTokenView.as_view(),name="text_morphological_token"),
]
