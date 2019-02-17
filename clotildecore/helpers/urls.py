from django.conf.urls import include, url
from django.conf import settings

from django.views.generic import DetailView,ListView

from . import views

urlpatterns =[
    url( r'^italiano/verbi/?$',views.ItalianoVerbiView.as_view(),name="italiano_verbi"),
]
