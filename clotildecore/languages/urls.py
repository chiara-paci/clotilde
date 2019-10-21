from django.conf.urls import include, url
from django.conf import settings

from django.views.generic import DetailView,ListView

from . import views,models
from morphology import models as morph_models

urlpatterns =[
    url( r'^language/?$',views.ListView.as_view(model=models.Language),
         name="language_list"),
    url( r'^language/(?P<pk>\d+)/?$',views.DetailView.as_view(model=models.Language),
         name="language_detail"),
    url( r'^language/(?P<pk>\d+)/roots/?$',views.ByLanguageListView.as_view(model_list=morph_models.Root),
         name="language_detail_roots"),
    url( r'^language/(?P<pk>\d+)/paradigmas/?$',
         views.ByLanguageListView.as_view(model_list=morph_models.Paradigma),
         name="language_detail_paradigmas"),
    url( r'^language/(?P<pk>\d+)/derivations/?$',
         views.ByLanguageListView.as_view(model_list=morph_models.Derivation),
         name="language_detail_derivations"),
    url( r'^language/(?P<pk>\d+)/fusions/?$',
         views.ByLanguageListView.as_view(model_list=morph_models.Fusion),
         name="language_detail_fusions"),
]
