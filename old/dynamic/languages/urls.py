from django.conf.urls import patterns, include, url
from django.conf import settings

from django.views.generic import DetailView,ListView

from languages.models import Language

urlpatterns =patterns('',
                      ( r'^/?$',
                        ListView.as_view(queryset=Language.objects.order_by('name'),
                                         context_object_name="language_list")),
                      ( r'^language/(?P<pk>\d+)/?$',
                        DetailView.as_view(model=Language,context_object_name="language")),
                      )
