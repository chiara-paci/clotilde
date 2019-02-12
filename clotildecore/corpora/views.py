# -*- coding: utf-8 -*-

from django.shortcuts import render
from django.views.generic import DetailView

import time
import re

from . import models

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
    template_name = "corpora/text_tokens.html"

    def get_context_data(self, **kwargs):
        context = TextView.get_context_data(self,**kwargs)
        regexp_set=self.object.corpus.language.token_regexp_set
        rexp_list,tokens=regexp_set.tokenize(self.object.text)
        context["style_list"]=rexp_list
        context["style_list"].append(["not matched","not-found","#900000","#ffffff","",""])
        context["token_list"]=tokens
        return context


class TextMorphologicalParserView(TextView):
    phase = "morphological_parser"

class TextMorphologicalTokenView(TextView):
    phase = "morphological_token"
