from django.shortcuts import render
from django.views.generic import DetailView,ListView

from . import models


# Create your views here.

class ByLanguageListView(DetailView):
    model = models.Language
    model_list = None

    def get(self,request,*args,**kwargs):
        language=self.get_object()
        inner_view=ListView.as_view(queryset=self.model_list.objects.filter(language=language))
        response=inner_view(request,*args,**kwargs)
        return response

