from django.conf.urls import include, url
from django.conf import settings

from django.views.generic import DetailView,ListView

from . import views,models

urlpatterns =[
    url( r'^paradigma/(?P<pk>\d+)/?$',views.ParadigmaView.as_view(),name="paradigma_detail"),
    url( r'^root/(?P<pk>\d+)/?$',DetailView.as_view(model=models.Root),name="root_detail"),
    url( r'^derivation/(?P<pk>\d+)/?$',DetailView.as_view(model=models.Derivation),name="derivation_detail"),
    url( r'^fusion/(?P<pk>\d+)/?$',DetailView.as_view(model=models.Fusion),name="fusion_detail"),
]
