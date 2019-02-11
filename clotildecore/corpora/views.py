# -*- coding: utf-8 -*-

from django.shortcuts import render
from django.views.generic import DetailView

import time
import re

from . import models
#from base import models as base_models

# def replace_newline(S,repl,preserve=False):
#     if not preserve:
#         for (r,n) in base_models.NEW_LINES:
#             S=S.replace(n,repl)
#         return(S)
#     for (r,n) in base_models.NEW_LINES:
#         S=S.replace(n,r+repl)
#     return(S)

# Create your views here.
class TextView(DetailView):
    model = models.Text
    phase = "text"

    def get_context_data(self, **kwargs):
        context = super(TextView, self).get_context_data(**kwargs)
        context['phase']=self.phase
        context['style_list']=[]
        context['text_html']=self.object.html()
        return context

class TextAlphaParserView(TextView):
    phase = "alpha_parser"

    def get_context_data(self, **kwargs):
        context = TextView.get_context_data(self,**kwargs)
        regexp_set=self.object.corpus.language.token_regexp_set
        rexp_list,tokens=regexp_set.tokenize(self.object.text)
        newtext="".join( [t.html() for t in tokens ] )
        context["style_list"]=rexp_list
        context["style_list"].append(["not matched","not-found","#900000","#ffffff","",""])
        context["text_html"]=newtext
        return context

class TextAlphaTokenView(TextView):
    phase = "alpha_token"

class TextMorphologicalParserView(TextView):
    phase = "morphological_parser"

class TextMorphologicalTokenView(TextView):
    phase = "morphological_token"
