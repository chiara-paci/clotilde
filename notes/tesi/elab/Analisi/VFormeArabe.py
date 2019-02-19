# -*- coding: utf-8 -*-

import gtk
import gtk.glade
import re
import cgi
import gobject
import os
import sys

from config import *
from GtkUtility import *
from VMenu  import MenuFormeArabe
from Glossario import VOttVariante,VoceOttomana
from Parola import Parola,ParSuffisso
from Suffissi import Suffisso
import utility

class VFormeArabe:
    def show(self): self.main.show()
    def destroy_function(self,obj): gtk.main_quit()

    def __init__(self,fname,fforme,fradici):
        self.glossario=None
        self.fname=fname
        self.fforme=fforme
        self.fradici=fradici

        self.dic={}
        self.dic["on_mainWindow_destroy"]=self.destroy_function

        self.mainxml=gtk.glade.XML(GLADES["formearabe"])
        self.mainxml.signal_autoconnect(self.dic)

        self.main=self.mainxml.get_widget("mainWindow")

	self.tvWork=self.mainxml.get_widget("tvWork")
	self.tvForme=self.mainxml.get_widget("tvForme")
	self.tvRadici=self.mainxml.get_widget("tvRadici")

        self.menu=MenuFormeArabe(self.mainxml)
        self.main.add_accel_group(self.menu.accel_group)
        self.menu.connect("file","quit",self.destroy_function)
        self.menu.connect("file","save",self.save)
        self.menu.connect("file","saveas",self.save_as)

        self.set_models()

    def save_as(self,obj):
        fname=get_filename_by_dialog(title="Forme arabe (main)")
        self.save_formearabe(fname)
        fname=get_filename_by_dialog(title="Forme")
        self.save_forme(fname)
        fname=get_filename_by_dialog(title="Radici")
        self.save_radici(fname)

    def save(self,obj):
        self.save_formearabe(self.fname)
        self.save_forme(self.fforme)
        self.save_radici(self.fradici)

    def save_formearabe(self,fname):
        fd=open(fname,'w')
        print "Opening "+fname
        for (p,(f,r,s)) in self.parole.items():
            fd.write(p+"@"+f+"@"+r+"\n")
        fd.close()

    def save_forme(self,fname):
        fd=open(fname,'w')
        print "Opening "+fname
        for (f,t,s,b) in self.forme.values():
            fd.write(f+"@"+t+"@"+s+"@"+b+"\n")
        fd.close()

    def save_radici(self,fname):
        fd=open(fname,'w')
        print "Opening "+fname
        for (r,s,b) in self.radici.values():
            fd.write(r+"@"+s+"@"+b+"\n")
        fd.close()

    def load(self):
        fd=open(self.fname,'r')
        comm_re=re.compile("%.*")
        self.parole={}
        self.radici={}
        self.forme={}
        for row in fd.readlines():
            r=row.replace("\n","").strip()
            if ( (not r) or (comm_re.match(r)) ): continue
            tokens=r.split("@")
            p=tokens[0]
            if len(tokens)==1:
                f=""
                r=""
            elif len(tokens)==2:
                f=tokens[1]
                r=""
            else:
                f=tokens[1]
                r=tokens[2]
            if bool(f) and not self.forme.has_key(f):
                self.forme[f]=[f,"","",""]
            if bool(r) and not self.radici.has_key(r):
                self.radici[r]=[r,"",""]
            self.parole[p]=[f,r,""]
        fd.close()

        fd=open(self.fforme,'r')
        for row in fd.readlines():
            r=row.replace("\n","").strip()
            if ( (not r) or (comm_re.match(r)) ): continue
            tokens=r.split("@")
            f=tokens[0]
            t=""
            s=""
            b=""
            if tokens[1]: t=tokens[1]
            if tokens[2]: s=tokens[2]
            if tokens[3]: b=tokens[3]
            if bool(f):
                if not self.forme.has_key(f):
                    self.forme[f]=[f,"","",""]
                self.forme[f][1]=t
                self.forme[f][2]=s
                self.forme[f][3]=b
        fd.close()
        self.model_forme.clear()
        map(self.model_forme.append,self.forme.values())

        fd=open(self.fradici,'r')
        for row in fd.readlines():
            r=row.replace("\n","").strip()
            if ( (not r) or (comm_re.match(r)) ): continue
            tokens=r.split("@")
            r=tokens[0]
            s=""
            b=""
            if tokens[1]: s=tokens[1]
            if tokens[2]: b=tokens[2]
            if bool(r):
                if not self.radici.has_key(r):
                    self.radici[r]=[r,"",""]
                self.radici[r][1]=s
                self.radici[r][2]=b
        fd.close()
        self.model_radici.clear()
        map(self.model_radici.append,self.radici.values())
        self.model.clear()
        map(lambda x: self.model.append([x[0],x[1][0],x[1][1],x[1][2]]),
            self.parole.items())

    def add_glossario(self,glossario):
        self.glossario=glossario
        for v in self.glossario.vociottomane:
            if v.origine.lower() not in ORIGINI_ARABE:
                continue
            if not self.parole.has_key(v.voce):
                self.parole[v.voce]=["","",v.significato]
            else:
                self.parole[v.voce][2]=v.significato
            for var in v.varianti:
                if not self.parole.has_key(var.voce):
                    if var.occasione:
                        sign="("+var.occasione+") "
                    else:
                        sign=""
                    sign+=v.significato
                    self.parole[var.voce]=["","",sign]
                else:
                    self.parole[var.voce][2]=v.significato
        self.model.clear()
        #print self.parole
        map(lambda x: self.model.append([x[0],x[1][0],x[1][1],x[1][2]]),
            self.parole.items())
        #print self.parole

    def sort_by_arabtex(self,S1,S2):
        if (S1==S2): return(0)
        if (S1=="="): return(-1)
        if (S2=="="): return(1)
        if (S1=="=="): return(-1)
        if (S2=="=="): return(1)
        if (S1=="==="): return(-1)
        if (S2=="==="): return(1)
        p1=Parola(S1,"Arabo")
        p2=Parola(S2,"Arabo")
        if p1<p2: return(-1)
        if p1>p2: return(1)
        return(0)

    def sort_func_by_arabtex(self,model,iter1,iter2,col_id):
        t1=model.get_value(iter1,col_id)
        t2=model.get_value(iter2,col_id)
        return(self.sort_by_arabtex(t1,t2))

    def cb_model_row_changed(self,model,path,iter):
        p=model.get_value(iter,0)
        f=model.get_value(iter,1)
        r=model.get_value(iter,2)
        if bool(f) and not self.forme.has_key(f):
            self.forme[f]=[f,"","",""]
            self.model_forme.append([f,"","",""])
        if bool(r) and not self.radici.has_key(r):
            self.radici[r]=[r,"",""]
            self.model_radici.append([r,"",""])
        self.parole[p][0]=f
        self.parole[p][1]=r

    def cb_model_forme_row_changed(self,model,path,iter):
        f=model.get_value(iter,0)
        t=model.get_value(iter,1)
        s=model.get_value(iter,2)
        b=model.get_value(iter,3)
        self.forme[f]=(f,t,s,b)

    def cb_model_radici_row_changed(self,model,path,iter):
        r=model.get_value(iter,0)
        s=model.get_value(iter,1)
        b=model.get_value(iter,2)
        self.radici[r]=(r,s,b)

    def set_models(self):
        self.model_forme=gtk.ListStore(str,str,str,str)
        self.model_radici=gtk.ListStore(str,str,str)
        self.model=gtk.ListStore(str,str,str,str)

        self.model_forme.append(["-","","",""])
        self.model_radici.append(["-","",""])

        self.model_forme.set_sort_func(0,self.sort_func_by_arabtex,0)
        self.model_radici.set_sort_func(0,self.sort_func_by_arabtex,0)
        self.model.set_sort_func(0,self.sort_func_by_arabtex,0)
        self.model.set_sort_func(1,self.sort_func_by_arabtex,1)
        self.model.set_sort_func(2,self.sort_func_by_arabtex,2)

        self.tvForme.set_model(self.model_forme)
        tvc=TreTransTVColumn("forme",0)
        self.tvForme.append_column(tvc)
        tvc=TextTVColumnEditable("tipo",1,self.model_forme)
        self.tvForme.append_column(tvc)
        tvc=TextTVColumnEditable("significato",2,self.model_forme)
        self.tvForme.append_column(tvc)
        tvc=TextTVColumnEditable("ref",3,self.model_forme)
        self.tvForme.append_column(tvc)

        self.tvRadici.set_model(self.model_radici)
        tvc=TreTransTVColumn("radici",0)
        self.tvRadici.append_column(tvc)
        tvc=TextTVColumnEditable("significato",1,self.model_radici)
        self.tvRadici.append_column(tvc)
        tvc=TextTVColumnEditable("ref",2,self.model_radici)
        self.tvRadici.append_column(tvc)

        self.model.connect("row-changed",self.cb_model_row_changed)
        self.model_radici.connect("row-changed",
                                  self.cb_model_radici_row_changed)
        self.model_forme.connect("row-changed",
                                 self.cb_model_forme_row_changed)
        self.tvWork.set_model(self.model)
        tvc=TreTransTVColumn("parole",0)
        self.tvWork.append_column(tvc)
        tvc=TreTransTVColumn("forme",1,
                             editable=True,model=self.model)
        self.tvWork.append_column(tvc)
        tvc=TreTransTVColumn("radici",2,
                             editable=True,model=self.model)
        self.tvWork.append_column(tvc)
        tvc=TextTVColumn("significato",3)
        self.tvWork.append_column(tvc)


    # a. tabella delle radici
    # b. tabella delle parole per forma

    def print_tabella_radici_tre(self,fd,perradici):
        rkeys=self.radici.keys()
        rkeys.sort(cmp=cfr_radici_arabe)
        reg=re.compile(".*=.*")

        R=filter(lambda x: (perradici.has_key(x) and not reg.match(x)),
                 rkeys)

        fd.write("\\clearpage\n\n")
        fd.write("\\twocolumn\n\n")

        fd.write("\\begin{footnotesize}\n")
        fd.write("\\begin{enumerate}\n")
        for r in R:
            fd.write("\\item ")
            fd.write(spzrl(r)+" ")
            fd.write(reftotex(self.radici[r][2],vuoto="\\hspace{1cm}")+"\n")
            fd.write("\\rigavuota\n")
            fd.write("\\begin{subvocedue}\n")
            for (p,f,s) in perradici[r]:
                fd.write("\\item["+spzrl(p)+"]")
                fd.write(s)
                fd.write("\n")
            fd.write("\\end{subvocedue}\n\n")
        fd.write("\\end{enumerate}\n\n")
        fd.write("\\end{footnotesize}\n\n")
        fd.write("\\onecolumn\n\n")
        fd.write("\\clearpage\n\n")

    def print_tabella_forme(self,fd,performe):
        rkeys=self.forme.keys()
        rkeys.sort(cmp=self.sort_by_arabtex)
        reg=re.compile(".*=.*")
        
        F=filter(lambda x: performe.has_key(x),rkeys)

        fd.write("\\clearpage\n\n")
        fd.write("\\twocolumn\n\n")
        
        fd.write("\\begin{footnotesize}\n")
        fd.write("\\begin{enumerate}\n")
        for f in F:
            fd.write("\\item ")
            if reg.match(f):
                fd.write(f+" ")
            else:
                fd.write(spzrl(f)+" ")
            fd.write(reftotex(self.forme[f][3],vuoto="\\hspace{1cm}")+"\n")
            fd.write("\\rigavuota\n")
            fd.write("\\begin{subvocedue}\n")
            for (p,r,s) in performe[f]:
                fd.write("\\item["+spzrl(p)+"]")
                fd.write(s)
                fd.write("(radice: "+spzrl(r)+")\n")
                fd.write("\n")
            fd.write("\\end{subvocedue}\n\n")
        fd.write("\\end{enumerate}\n\n")
        fd.write("\\end{footnotesize}\n\n")
        fd.write("\\onecolumn\n\n")
        fd.write("\\clearpage\n\n")

    def print_tabella_radici(self,fd,perradici):
        rkeys=self.radici.keys()
        rkeys.sort(cmp=cfr_radici_arabe)
        Ncol=2
        Nrow=35
        tabdef="l|*{"+str(Ncol)+"}{rlp{2.8cm}l|}"
        reg=re.compile(".*=.*")

        TABS=[]
        R=[]
        TAB=[]
        n=1
        nr=1
        for r in rkeys:
            if not perradici.has_key(r): continue
            if reg.match(r): continue
            R.append(r)
            if not (n%Ncol):
                TAB.append(R)
                R=[]
                if not (nr%Nrow):
                    TABS.append(TAB)
                    TAB=[]
                nr+=1
            n+=1

        NEWTABS=[]

        for tab in TABS:
            R=len(tab)
            C=len(tab[0])
            newtab=map(lambda x: map(lambda x: "",range(0,C)),range(0,R))
            nr=0
            nc=0
            for row in tab:
                for x in row:
                    newtab[nr][nc]=x
                    nr+=1
                    if nr<R: continue
                    nr=0
                    nc+=1
            NEWTABS.append(newtab)
        TABS=NEWTABS
        nr=1
        fd.write("\\begin{small}\n")
        for (tab) in TABS:
            fd.write("\\noindent\\begin{tabular}{"+tabdef+"}\n")
            for row in tab:
                fd.write(str(nr))
                for r in row:
                    fd.write("&"+spzrltab(r))
                    fd.write("&"+self.radici[r][1])
                    fd.write("&"+reftotex(self.radici[r][2],vuoto="\\hspace{1cm}"))
                nr+=1
                fd.write("\\\\\n\\hline\n")
            fd.write("\\end{tabular}\n\n")
        fd.write("\\end{small}\n\n")

    def print_senza_radice(self,fd,perradici):
        rkeys=self.radici.keys()
        rkeys.sort(cmp=cfr_radici_arabe)

        Ra=filter(lambda x: (perradici.has_key(x) and (x=="=")),
                  rkeys)
        Rb=filter(lambda x: (perradici.has_key(x) and (x=="===")),
                  rkeys)

        fd.write("\\begin{footnotesize}\n")
        fd.write("\\begin{enumerate}\n")
        fd.write("\\item Immotivate:\n")
        fd.write("\\begin{subvocedue}\n")
        for r in Ra:
            for (p,f,s) in perradici[r]:
                fd.write("\\item["+spzrl(p)+"]")
                fd.write(s)
                fd.write("\n")
        fd.write("\\end{subvocedue}\n\n")
        fd.write("\\item Non arabe:\n")
        fd.write("\\begin{subvocedue}\n")
        for r in Rb:
            for (p,f,s) in perradici[r]:
                fd.write("\\item["+spzrl(p)+"]")
                fd.write(s)
                fd.write("\n")
        fd.write("\\end{subvocedue}\n\n")

        fd.write("\\end{enumerate}\n\n")
        fd.write("\\end{footnotesize}\n\n")

    def print_tex(self,fd):
        perradici={}
        performe={}

        for (p,[f,r,s]) in self.parole.items():
            if not r: r="-"
            if not f: f="-"
            if not perradici.has_key(r): perradici[r]=[]
            if not performe.has_key(f): performe[f]=[]

            perradici[r].append((p,f,s))
            performe[f].append((p,r,s))

        fd.write("\\section{Parole di origine araba}\n\n")

        self.print_senza_radice(fd,perradici)

        #self.print_tabella_radici(fd,perradici)
        fd.write("\n\\clearpage\n")
        self.print_tabella_forme(fd,performe)

        fd.write("\n\\clearpage\n")

        self.print_tabella_radici_tre(fd,perradici)

        return

        fd.write("\\subsection{Per radici}\n\n")

        
        #fd.write("\\begin{itemize*}\n")
        #for r in perradici.keys():
        #    if r=="-":
        #        fd.write("\\item Radici non assegnate\n")
        #    else:
        #        fd.write("\\item "+spzrl(r)+"\n\n")
        #    fd.write("\\begin{itemize*}\n")
        #    for (p,f) in perradici[r]:
        #        fd.write("\\item "+spzrl(f)+" "+spzrl(p)+"\n")
        #    fd.write("\\end{itemize*}\n")
        #fd.write("\\end{itemize*}\n")

        fd.write("\\subsection{Per forme}\n\n")
        
        #fd.write("\\begin{itemize*}\n")
        tab=False
        for f in performe.keys():
            tab=False
            if f=="-":
                fd.write("\\clearpage\n")
                #fd.write("\\item Forme non assegnate\n")
                tab=True
            #elif f=="=":
            #    fd.write("\\item Senza radice\n")
            #elif f=="==":
            #    fd.write("\\item Composti\n")
            #elif f=="===":
            #    fd.write("\\item Persiani\n")
            #else:
                #fd.write("\\item "+spzrl(f)+"\n\n")
            #    continue
            if not tab:
                #fd.write("\\begin{itemize*}\n")
                #for (p,r) in performe[f]:
                #    fd.write("\\item "+spzrl(r)+" "+spzrl(p)+"\n")
                #fd.write("\\end{itemize*}\n")
                continue

            NC=3
            fd.write("\n\n\\noindent\\begin{tabular}{|*{"+str(NC)+"}{rlc|}}\n")
            n=0
            for (p,r) in performe[f]:
                fd.write(spzrltab(p))
                fd.write("& \mbox{ }\hspace{3em}\mbox{ }")
                if bool((n+1)%NC): fd.write("&")
                else: fd.write("\\\\\n\\hline\n")
                n+=1
            #fd.write("\\\\\n\\hline\n")
            fd.write("\\end{tabular}\n")
            fd.write("\\clearpage\n")
            
        #fd.write("\\end{itemize*}\n")

