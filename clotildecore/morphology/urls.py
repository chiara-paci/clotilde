from django.conf.urls import include, url
from django.conf import settings

from django.views.generic import DetailView,ListView

from . import views,models

urlpatterns =[
    url( r'^$',ListView.as_view(model=models.Paradigma),name="index"),
    
    url( r'^paradigma/?$',ListView.as_view(model=models.Paradigma),name="paradigma_list"),
    url( r'^paradigma/(?P<pk>\d+)/?$',views.ParadigmaView.as_view(),name="paradigma_detail"),

    url( r'^root/?$',ListView.as_view(model=models.Root),name="root_list"),
    url( r'^root/(?P<pk>\d+)/?$',DetailView.as_view(model=models.Root),name="root_detail"),

    url( r'^derivation/?$',ListView.as_view(model=models.Derivation),name="derivation_list"),
    url( r'^derivation/(?P<pk>\d+)/?$',DetailView.as_view(model=models.Derivation),name="derivation_detail"),

    url( r'^fusion/?$',ListView.as_view(model=models.Fusion),name="fusion_list"),
    url( r'^fusion/(?P<pk>\d+)/?$',DetailView.as_view(model=models.Fusion),name="fusion_detail"),

    url( r'^tema/?$',ListView.as_view(model=models.Tema),name="tema_list"),
    url( r'^tema/(?P<pk>\d+)/?$',DetailView.as_view(model=models.Tema),name="tema_detail"),

]
