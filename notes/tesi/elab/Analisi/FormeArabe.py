# -*- coding: utf-8 -*-

from config import *
import os
import re
from Parola import Parola
import sys
from GRiga import GRiga

class FormaAraba(GRiga):
    def __init__(self,data):
        GRiga.__init__(self,data,0,"formaaraba","Forme Arabe")
        (self.voce,self.categoria,self.significato,sfonte)=self.args
        self.references=self.split_references(sfonte)

    def pron_valutazione(self):
        if not self.references_pron:
            return(0.0)
        else:
            return(1.0)

    def print_item(self,fd,bullet="",color=""):
        if color:
            if bullet: bullet="{\\color{"+color+"}"+bullet+"}"
            txt="{\\color{"+color+"}"+spzrl(self.voce.strip())+"}"
        else:
            txt=spzrl(self.voce.strip())
        if bullet:
            fd.write("\\item["+bullet+"] "+txt)
        else:
            fd.write("\\item["+txt+"]")
        conv=[]
        if self.categoria:
            fd.write(", "+self.categoria.lower().strip()+".")
        if self.significato:
            fd.write("; "+self.significato.strip())
        fd.write("\n")
        fd.write("\\begin{subvocedue}\n")
        self.print_ref(fd,self.references,"Rif.")
        fd.write("\\end{subvocedue}\n")

class FormeArabe(list):
    def __init__(self,finput):
        self.finput=finput
        list.__init__(self)

    def load(self):
        if not self.finput: return
        if self.finput=="-":
            fd=sys.stdin
        else:
            if not os.path.exists(self.finput): return
            fd=open(self.finput,'r')
        self.clear()
        righekeys=[ "formaaraba" ]
        tipo_re=re.compile("^.([^{[ ]*)[{[].*")
        cont_re=re.compile("^ .*")
        comm_re=re.compile("%.*")
        currenttxt=""
        for row in fd.readlines(): 
            r=row.replace("\n","").strip()
            if ( (not r) or (comm_re.match(r)) ):
                s=FormaAraba(currenttxt)
                currenttxt=""
                self.append(s)
                continue
            if cont_re.match(row):
                if currenttxt:
                    currenttxt+=" "+r
                continue
            t=tipo_re.findall(r)
            if ( (not t) or (t[0] not in righekeys) ):
                s=FormaAraba(currenttxt)
                currenttxt=""
                self.append(s)
                continue
            if currenttxt:
                s=FormaAraba(currenttxt)
                self.append(s)
            currenttxt=r
        s=FormaAraba(currenttxt)
        self.append(s)
        if self.finput!="-":
            fd.close()
        self.sort()
