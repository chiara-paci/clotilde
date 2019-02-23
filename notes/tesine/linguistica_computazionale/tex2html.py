#!/usr/bin/python


import json

OUTDIR="html"
INFILE="dbrelazionale.tex"

fd=open(INFILE)

status="no"
flist=[]
txt=[]

for r in fd.readlines():
    r=r.strip()
    if status=="no":
        if not r.startswith(r'\section'): continue
        status="yes"
    if r.startswith("%%%%%%%%%"):
        flist.append(txt)
        break
    if not r.startswith(r'\section'):
        txt.append(r)
        continue
    if txt:
        flist.append(txt)
    txt=[r]

fd.close()

class Section(object):
    def __init__(self,title,order): 
        self.title=title
        self.order=order
        self.page=self._slugify(title)
        self.label=""
        self.txt=[]

    def _slugify(self,t):
        x=t.strip().lower()
        x=x.replace(" ","-")
        x=x.replace("'","-")
        return x

    def html(self):
        S="---\n"
        S+="title: %s\n" % self.title
        S+="layout: default\n"
        if self.label:
            S+='label: sec_%s\n' % self.label
        S+="url: /page/%s\n" % self.page
        S+="---\n"

        ret=[]
        for t in "\n".join(self.txt).split("<br/>"):
            t=t.strip()
            if not t: continue
            if t.startswith("<"):
                ret.append(t)
                continue
            ret.append("<p>%s</p>" % t )
        

        return S+"\n".join(ret)

    def outline(self):
        return {
            "order": self.order,
            "label": self.label,
            "toc": self.title,
            "url": "/page/%s\n" % self.page
        }
        

sections=[]
order=1
for txt in flist:
    title=txt[0].replace('\\section{','').replace('}','')
    sec=Section(title,order)
    order+=1
    sec.label=txt[1].replace('\\label{sec:','').replace('}','')
    sec.txt=[]
    eopen=False
    for r in txt[2:]:
        if r=='\\begin{enumerate}':
            sec.txt.append("<br/>")
            sec.txt.append("<ol>")
            sec.txt.append("")
            continue
        if r=='\\end{enumerate}':
            sec.txt.append("</li>")
            sec.txt.append("</ol>")
            sec.txt.append("<br/>")
            sec.txt.append("")
            continue
        if r=='\\begin{itemize}':
            sec.txt.append("<br/>")
            sec.txt.append("<ul>")
            sec.txt.append("")
            continue
        if r=='\\end{itemize}':
            sec.txt.append("</li>")
            sec.txt.append("</ul>")
            sec.txt.append("<br/>")
            sec.txt.append("")
            continue
        if r.startswith("\\item"):
            if not sec.txt[-1]:
                sec.txt[-1]+="<li>"
            else:
                sec.txt.append("</li>")
                sec.txt.append("<li>")
            sec.txt.append( r.replace('\\item','') )
            continue
        if r.startswith('\\subsection'):
            t=r.replace('\\subsection{','').replace('}','')
            sec.txt.append("<br/>")
            sec.txt.append("<h2>%s</h2>" % t)
            sec.txt.append("")
            continue
        if r.startswith('\\subsubsection'):
            t=r.replace('\\subsubsection{','').replace('}','')
            sec.txt.append("<br/>")
            sec.txt.append("<h3>%s</h3>" % t)
            sec.txt.append("")
            continue
        if r.startswith('\\myfig'):
            sec.txt.append("<br/>")
            sec.txt.append("<figure>%s</figure>" % r)
            sec.txt.append("<br/>")
            sec.txt.append("")
            continue
        if r.startswith('\\begin{tabular}'):
            t=r.replace('\\begin{tabular}','').strip()
            sec.txt.append("<br/>")
            sec.txt.append("<table>%s" % t)
            sec.txt.append("")
            continue
        if r.startswith('\\end{tabular}'):
            t=r.replace('\\end{tabular}','').strip()
            sec.txt.append("%s</table>" % t)
            sec.txt.append("<br/>")
            sec.txt.append("")
            continue
        if r.startswith('\\begin'):
            sec.txt.append("<br/>")
            sec.txt.append("<pre>%s" % r)
            sec.txt.append("")
            continue
        if r.startswith('\\end'):
            sec.txt[-1]+="%s</pre>" % r
            sec.txt.append("<br/>")
            sec.txt.append("")
            continue
        if r.startswith('\\label{sec:'):
            t=r.replace('\\label{sec:','').replace('}','')
            sec.txt.append("<a name='%s'></a>" % t)
            sec.txt.append("<br/>")
            sec.txt.append("")
            continue
        if r=="}":
            sec.txt[-1]+=r
            sec.txt.append("")
            continue
        if not r:
            sec.txt.append("<br/>")
            sec.txt.append("")
            continue

        if sec.txt:
            sec.txt[-1]+=" "+r
        else:
            sec.txt.append(r)
    sections.append(sec)


outline=[]
for sec in sections:
    outline.append(sec.outline())
    fd=open("%s/%s.html" % (OUTDIR,sec.page),"w")
    fd.write(sec.html())
    fd.close()

print(outline)

fd=open("%s/outline.json" % OUTDIR,"w")
json.dump(outline,fd)
fd.close()


