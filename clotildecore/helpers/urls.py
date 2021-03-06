from django.conf.urls import include, url
from django.conf import settings

from django.views.generic import DetailView,ListView

from . import views

app_name="helpers"

urlpatterns =[
    url( r'^italiano/?$',views.ItalianoView.as_view(),name="italiano"),
    url( r'^italiano/textcollector/(?P<pk>\d+)/?$',
         views.ItalianoTextCollectorView.as_view(),name="italiano_textcollector"),
    url( r'^italiano/verbi/?$',views.ItalianoVerbiView.as_view(),name="italiano_verbi"),
    url( r'^italiano/add_root/?$',views.ItalianoAddRootView.as_view(),name="italiano_add_root"),
    url( r'^italiano/paradigma_nome/?$',views.ParadigmaView.as_view(part_of_speech="nome"),name="italiano_paradigma_nome"),
    url( r'^italiano/paradigma_verbo/?$',views.ParadigmaView.as_view(part_of_speech="verbo"),name="italiano_paradigma_verbo"),
]
