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

    def build_text(self):
        style_list,tokens=self.object.corpus.language.alpha_tokenize(self.object.text)
        newtext="".join( [t.html() for t in tokens ] )
        return style_list,newtext

    def get_context_data(self, **kwargs):
        context = TextView.get_context_data(self,**kwargs)

        style_list,newtext=self.build_text()

        context["style_list"]=style_list
        context["text_html"]=newtext
        return context

class TextAlphaTokenView(TextView):
    phase = "alpha_token"
    template_name = "corpora/text_tokens.html"

    def build_token_list(self):
        style_list,tokens=self.object.corpus.language.alpha_tokenize(self.object.text)
        tokens=list(set(tokens))
        tokens.sort()
        return style_list,tokens

    def get_context_data(self, **kwargs):
        context = TextView.get_context_data(self,**kwargs)

        style_list,tokens=self.build_token_list()

        context["style_list"]=style_list
        context["token_list"]=tokens
        return context


class TextMorphologicalParserView(TextAlphaParserView):
    phase = "morphological_parser"

    def build_text(self):
        style_list,tokens=self.object.corpus.language.morph_tokenize(self.object.text)
        newtext="".join( [t.html() for t in tokens ] )
        return style_list,newtext

class TextMorphologicalTokenView(TextAlphaTokenView):
    phase = "morphological_token"
    template_name = "corpora/text_tokens_morphology.html"

    def build_token_list(self):
        style_list,tokens=self.object.corpus.language.morph_tokenize(self.object.text)
        tokens=list(set(tokens))
        tokens.sort()
        return style_list,tokens
