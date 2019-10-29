from django.shortcuts import render

from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.http import JsonResponse,Http404
from django import forms
from django.http import HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt,csrf_protect
from django.utils.decorators import method_decorator

from django.views.generic import DetailView,ListView

# Create your views here.

from . import models

@method_decorator(csrf_exempt,name="dispatch")
class ParadigmaView(DetailView):
    model = models.Paradigma

    def get(self,request,*args,**kwargs):
        self.object=self.get_object()
        obj={ "name": self.object.name }
        obj["inflections"]=[ infl.serialize() for infl in self.object.inflections.all() ]
        response=JsonResponse(obj,status=200)
        return response

class ByLanguageListView(ListView):
    def get_queryset(self):
        pk=self.kwargs.get('pk')
        return self.model.objects.by_language(pk)
