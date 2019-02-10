# Create your views here.
from django.shortcuts import render_to_response,get_object_or_404
from django.template import RequestContext
from django.conf import settings
from django.shortcuts import render
from django.views.generic.base import View
from django.views.generic import DetailView

from corpora.models import *
from base.models import MARKERS,NEW_LINES

import re,time

def replace_newline(S,repl,preserve=False):
    if not preserve:
        for (r,n) in NEW_LINES:
            S=S.replace(n,repl)
        return(S)
    for (r,n) in NEW_LINES:
        S=S.replace(n,r+repl)
    return(S)

LF_IMG='<img src="/lf.png"/>'
END_IMG='<img src="/end.png"/>'
BEGIN_IMG='<img src="/begin.png"/>'

class TextView(DetailView):
    def get_context_data(self, **kwargs):
        context = super(TextView, self).get_context_data(**kwargs)
        context.update({'phase_text': True})
        return context

class AlphaParserView(View):
    #def get(self, request, text_id):
    #    text=get_object_or_404(Text,id=text_id)
    #    return render(request,"corpora/text_detail.html",{"text": text})

    def get(self,request,text_id):
        t0=time.time()
        text=get_object_or_404(Text,id=text_id)
        regexp_set=text.corpus.language.token_regexp_set
        c=re.compile(regexp_set.regexp_all())
        tokens=filter(bool,c.split(text.text))
        rexp_list=regexp_set.regexp_objects()

        L=len(tokens)
        t1=time.time()
        print "prima fase ok numtok=%d, sec.=%4.4f" % (L,t1-t0)

        def f(t):
            for (name,label,bg,fg,rexp,rexp_t) in rexp_list:
                if rexp.match(t):
                    T='<span class="'+label+'"> '
                    t=t.replace(" ","&nbsp;")
                    t=replace_newline(t," "+LF_IMG+"<br/>\n")
                    T+=t
                    T+="</span>"
                    return(T)
            if t[0]=='[':
                if t[1]=="/":
                    m=t[2:-1]
                    T='<img src="'+settings.CLOTILDE_ICONS_MARKERS_PATH+'/'+m+'.png"/>'
                    T+=END_IMG
                else:
                    m=t[1:-1]
                    T=BEGIN_IMG
                    T+='<img src="'+settings.CLOTILDE_ICONS_MARKERS_PATH+'/'+m+'.png"/>'
                if m in MARKERS:
                    return(T)
            t=t.replace(" ","&nbsp;")
            t=replace_newline(t," "+LF_IMG+"<br/>\n")
            T='<span class="not-found"> '
            T+=t
            T+="</span>"
            return(T)
        
        newtext=""
        n=1
        for t in tokens:
            ta=time.time()
            newtext+=f(t)
            tb=time.time()
            print "%d/%d %4.4f" % (n,L,tb-ta)
            n+=1
        t2=time.time()
        print "seconda fase ok - sec.=%4.4f" % (t2-t1)
        t3=time.time()
        print "terza fase ok - sec.=%4.4f" % (t3-t2)
        params={}
        params["rexp_list"]=rexp_list
        # aggiungere style per not-found (name=not matched)
        # 
        # span.not-found {
        #     color: #ffffff;
        #     background-color: #900000;
        #     border-left: 1px solid #ffffff;
        #     padding-right: 1em;
        # }

        params["style_list"]=map(lambda (name,label,bg,fg,rexp,rexp_t): (name+': '+rexp_t,label,fg,bg),rexp_list)
        params["text"]=text
        params["regexp_set"]=regexp_set
        params["newtext"]=newtext
        params["phase_alpha_p"]=True
        return render_to_response("corpora/text_detail_alpha_parsed.html", context=params)




# def alpha_parser(request,text_id):
#     t0=time.time()
#     text=get_object_or_404(Text,id=text_id)
#     regexp_set=text.corpus.language.token_regexp_set
#     c=re.compile(regexp_set.regexp_all())
#     tokens=filter(bool,c.split(text.text))
#     rexp_list=regexp_set.regexp_objects()

#     L=len(tokens)
#     t1=time.time()
#     print "prima fase ok numtok=%d, sec.=%4.4f" % (L,t1-t0)

#     def f(t):
#         for (name,label,bg,fg,rexp,rexp_t) in rexp_list:
#             if rexp.match(t):
#                 T='<span class="'+label+'"> '
#                 t=t.replace(" ","&nbsp;")
#                 t=replace_newline(t," "+LF_IMG+"<br/>\n")
#                 T+=t
#                 T+="</span>"
#                 return(T)
#         if t[0]=='[':
#             if t[1]=="/":
#                 m=t[2:-1]
#                 T='<img src="'+settings.CLOTILDE_ICONS_MARKERS_PATH+'/'+m+'.png"/>'
#                 T+=END_IMG
#             else:
#                 m=t[1:-1]
#                 T=BEGIN_IMG
#                 T+='<img src="'+settings.CLOTILDE_ICONS_MARKERS_PATH+'/'+m+'.png"/>'
#             if m in MARKERS:
#                 return(T)
#         t=t.replace(" ","&nbsp;")
#         t=replace_newline(t," "+LF_IMG+"<br/>\n")
#         T='<span class="not-found"> '
#         T+=t
#         T+="</span>"
#         return(T)
        
#     newtext=""
#     n=1
#     for t in tokens:
#         ta=time.time()
#         newtext+=f(t)
#         tb=time.time()
#         print "%d/%d %4.4f" % (n,L,tb-ta)
#         n+=1
#     t2=time.time()
#     print "seconda fase ok - sec.=%4.4f" % (t2-t1)
#     t3=time.time()
#     print "terza fase ok - sec.=%4.4f" % (t3-t2)
#     params={}
#     params["rexp_list"]=rexp_list
#     params["style_list"]=map(lambda (name,label,bg,fg,rexp,rexp_t): (name+': '+rexp_t,label,fg,bg),rexp_list)
#     params["text"]=text
#     params["regexp_set"]=regexp_set
#     params["newtext"]=newtext
#     return render_to_response("corpora/text_detail_parsed.html", params,
#                               context_instance=RequestContext(request))

def alpha_token(request,text_id):
    t0=time.time()
    text=get_object_or_404(Text,id=text_id)
    language=text.corpus.language
    regexp_set=language.token_regexp_set
    c=re.compile(regexp_set.regexp_all())
    tokens=list(set(filter(bool,c.split(text.text))))
    tokens.sort()
    rexp_list=regexp_set.regexp_objects()

    L=len(tokens)
    t1=time.time()
    print "prima fase ok numtok=%d, sec.=%4.4f" % (L,t1-t0)

    def f(t):
        for (name,label,bg,fg,rexp,rexp_t) in rexp_list:
            if rexp.match(t):
                t=t.replace(" ","&nbsp;")
                t=replace_newline(t," "+LF_IMG+"<br/>\n")
                return(label,name,t)
        if t[0]=='[':
            if t[1]=="/":
                m=t[2:-1]
                T='<img src="'+settings.CLOTILDE_ICONS_MARKERS_PATH+'/'+m+'.png"/>'
                T+=END_IMG
            else:
                m=t[1:-1]
                T=BEGIN_IMG
                T+='<img src="'+settings.CLOTILDE_ICONS_MARKERS_PATH+'/'+m+'.png"/>'
            if m in MARKERS:
                return("marker","marker",T)
        t=t.replace(" ","&nbsp;")
        t=replace_newline(t," "+LF_IMG+"<br/>\n")
        return("not-found","not found",t)
        
    token_list=[]
    n=1
    for t in tokens:
        ta=time.time()
        token_list.append(f(t))
        tb=time.time()
        print "%d/%d %4.4f" % (n,L,tb-ta)
        n+=1
    t2=time.time()
    print "seconda fase ok - sec.=%4.4f" % (t2-t1)
    t3=time.time()
    print "terza fase ok - sec.=%4.4f" % (t3-t2)
    params={}
    params["rexp_list"]=rexp_list
    params["style_list"]=map(lambda (name,label,bg,fg,rexp,rexp_t): (name+': '+rexp_t,label,fg,bg),rexp_list)
    params["text"]=text
    params["regexp_set"]=regexp_set
    params["token_list"]=token_list
    params["rowtemplate"]="corpora/includes/alpha_token_rows.html"
    return render_to_response("corpora/text_detail_token.html", context=params)
