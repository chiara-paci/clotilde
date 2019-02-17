from django.conf.urls import include, url
from django.conf import settings

from django.views.generic import DetailView,ListView

from . import views

urlpatterns =[
    url( r'^paradigma/(?P<pk>\d+)/?$',views.ParadigmaView.as_view(),name="paradigma_detail"),
]
