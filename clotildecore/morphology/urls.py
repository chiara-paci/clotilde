from django.conf.urls import include, url
from django.conf import settings

from django.views.generic import DetailView,ListView

from . import views,models
from languages import models as lang_models

app_name="morphology"

urlpatterns =[
    url( r'^$',
         ListView.as_view(model=lang_models.Language,
                          template_name="morphology/language_list.html"),
         name="index"),
    url( r'^language/(?P<pk>\d+)/?$',
         DetailView.as_view(model=lang_models.Language,
                            template_name="morphology/language_detail.html"),
         name="index_language"),

    url( r'^language/(?P<pk>\d+)/paradigma/?$',
         views.ByLanguageListView.as_view(model=models.Paradigma),name="paradigma_language_list"),
    url( r'^paradigma/?$',ListView.as_view(model=models.Paradigma),name="paradigma_list"),
    url( r'^paradigma/(?P<pk>\d+)/?$',views.ParadigmaView.as_view(),name="paradigma_detail"),

    url( r'^dictionary/?$',ListView.as_view(model=lang_models.Language,
                                            template_name="morphology/dictionary_list.html"),
         name="dictionary_list"),
    url( r'^dictionary/(?P<pk>\d+)/?$',DetailView.as_view(model=lang_models.Language,
                                                          template_name="morphology/dictionary_detail.html"),
         name="dictionary_detail"),
]

for k,model in [ ("tema",models.Tema),
                 ("root",models.Root),
                 ("derivation",models.Derivation),
                 ("fusion",models.Fusion),
                 ("stem",models.Stem) ]: 
    urlpatterns += [
        url( r'^language/(?P<pk>\d+)/'+k+'/?$',
             views.ByLanguageListView.as_view(model=model),name=k+"_language_list"),
        url( r'^'+k+'/?$',ListView.as_view(model=model),name=k+"_list"),
        url( r'^'+k+'/(?P<pk>\d+)/?$',DetailView.as_view(model=model),name=k+"_detail"),
    ]
    


