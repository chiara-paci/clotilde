# -*- coding: utf-8 -*-

from django.shortcuts import render
from django.views.generic import DetailView

import time
import re

from . import models
from base import models as base_models

def replace_newline(S,repl,preserve=False):
    if not preserve:
        for (r,n) in base_models.NEW_LINES:
            S=S.replace(n,repl)
        return(S)
    for (r,n) in base_models.NEW_LINES:
        S=S.replace(n,r+repl)
    return(S)

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

        t0=time.time()
        regexp_set=self.object.corpus.language.token_regexp_set
        c=re.compile(regexp_set.regexp_all())
        tokens=list(filter(bool,c.split(self.object.text)))
        rexp_list=regexp_set.regexp_objects()

        L=len(tokens)
        t1=time.time()
        print("prima fase ok numtok=%d, sec.=%4.4f" % (L,t1-t0))

        def f(t):
            for (name,label,bg,fg,rexp,rexp_t) in rexp_list:
                if rexp.match(t):
                    t=t.replace(" ","&nbsp;")
                    t=replace_newline(t,"¶<br/>\n")
                    if not t: t="&nbsp;"
                    T='<span class="token '+label+'"> '
                    T+=t
                    T+="</span>"
                    return T
            if t[0]=='[':
                if t[1]=="/":
                    m=t[2:-1]
                    T='<span class="token"><i class="fas fa-arrow-alt-circle-left"></i></span>'
                else:
                    m=t[1:-1]
                    T='<span class="token"><i class="fas fa-arrow-alt-circle-right"></i></span>'
                if m in base_models.MARKERS:
                    return(T)
            t=t.replace(" ","&nbsp;")
            t=replace_newline(t,"¶<br/>\n")
            if not t: t="&nbsp;"
            T='<span class="not-found"> '
            T+=t
            T+="</span>"
            return(T)
        
        newtext=""
        newtext="".join( [ f(t) for t in tokens ] )
        t2=time.time()
        print("seconda fase ok - sec.=%4.4f" % (t2-t1))
        # aggiungere style per not-found (name=not matched)
        # 
        # span.not-found {
        #     color: #ffffff;
        #     background-color: #900000;
        #     border-left: 1px solid #ffffff;
        #     padding-right: 1em;
        # }

        context["style_list"]=[ (name+': '+rexp_t,label,fg,bg) for name,label,bg,fg,rexp,rexp_t in rexp_list ]
        context["text_html"]=newtext
        #params["regexp_set"]=regexp_set
        #params["newtext"]=newtext
        return context




class TextAlphaTokenView(TextView):
    phase = "alpha_token"

class TextMorphologicalParserView(TextView):
    phase = "morphological_parser"

class TextMorphologicalTokenView(TextView):
    phase = "morphological_token"
