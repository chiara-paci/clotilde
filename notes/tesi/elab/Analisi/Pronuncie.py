# -*- coding: utf-8 -*-

from config import *
import os
import re
from Parola import Parola,ParSuffisso
from Voci import VoceOttomana,VOttVariante
import sys
from GRiga import GRiga
from GMatch           import GMatchSimil,GMatchRadice,GMatchPrefix

class Pronuncia(GRiga):
    def __init__(self,data):
        GRiga.__init__(self,data,0,"pronuncia","Turco")
        self.split_args()
        self.voci=[]

    def split_args(self):
        (self.voce,pfonte,self.pronuncia)=self.args
        self.references_pron=self.split_references(pfonte)

    def save_item(self,fd,tipo=""):
        if not tipo: tipo=self.tipo
        pfonte=self.join_references(self.references_pron)
        args=[self.voce,pfonte,self.pronuncia]
        txt="\\pronuncia"
        txt+="{"+"}{".join(args)+"}\n"
        fd.write(txt)

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
        if self.pronuncia.strip():
            pron=" {\\sf "+self.pronuncia.strip()+"}"
            virg=","
        else:
            pron=""
            virg=""
        if bullet:
            fd.write("\\item["+bullet+"] "+txt+virg+pron)
        else:
            fd.write("\\item["+txt+virg+"]"+pron)
        fd.write("\n")
        fd.write("\\begin{subvocedue}\n")
        self.print_ref(fd,self.references_pron,
                       "Pron. ("+str(self.pron_valutazione())+")")
        fd.write("\\end{subvocedue}\n")

class Pronuncie(list):
    def __init__(self,finput,defref):
        self.finput=finput
        self.defref=defref
        self.glossario=None
        list.__init__(self)

    def save(self,fd=None):
        if not fd:
            if not self.finput: return
            if self.finput=="-":
                fd=sys.stdout
            else:
                if not os.path.exists(self.finput): return
                fd=open(self.finput,'w')
        fd.write("% suffissi\n")
        fd.write("\n")
        for p in self:
            p.save_item(fd)
        if self.finput!="-":
            fd.close()

    def clear(self):
        list.__init__(self)

    def load(self):
        if not self.finput: return
        if self.finput=="-":
            fd=sys.stdin
        else:
            if not os.path.exists(self.finput): return
            fd=open(self.finput,'r')
        self.clear()
        righekeys=[ "pronuncia" ]
        tipo_re=re.compile("^.([^{[ ]*)[{[].*")
        cont_re=re.compile("^ .*")
        comm_re=re.compile("%.*")
        currenttxt=""
        for row in fd.readlines(): 
            r=row.replace("\n","").strip()
            if ( (not r) or (comm_re.match(r)) ):
                if currenttxt:
                    s=Pronuncia(currenttxt)
                    self.append(s)
                currenttxt=""
                continue
            if cont_re.match(row):
                if currenttxt:
                    currenttxt+=" "+r
                continue
            t=tipo_re.findall(r)
            if ( (not t) or (t[0] not in righekeys) ):
                if currenttxt:
                    s=Pronuncia(currenttxt)
                    self.append(s)
                currenttxt=""
                continue
            if currenttxt:
                s=Pronuncia(currenttxt)
                self.append(s)
            currenttxt=r
        if currenttxt:
            s=Pronuncia(currenttxt)
            self.append(s)
        if self.finput!="-":
            fd.close()
        self.sort()

    def add_glossario(self,glossario):
        self.glossario=glossario
        self.solo_gloss=[]

        for v in self.glossario.get_all():
            trovato=False
            for p in self:
                if v.simil(p):
                    p.voci.append(p)
                    trovato=True
            if not trovato:
                self.solo_gloss.append(v)

    def match_glossario(self,glossario):
        self.glossario=glossario

        for v in self.glossario.get_all():
            trovato=False
            for p in self:
                if v.simil(p):
                    print v.voce,p.pronuncia
                    trovato=True
                    
    def load_g2p(self,fname):
        if fname=="-":
            fd=sys.stdin
        else:
            if not os.path.exists(fname): return
            fd=open(fname,'r')
        g2plist=[]
        atex_re=re.compile(".*([:^_.]|aT|[aui]N).*")
        for row in fd.readlines():
            r=row.replace("\n","").strip()
            if not r: continue
            tokens=r.split(" ")
            word=tokens[0]
            if not atex_re.match(word):
                word=self.from_g2p(word)
            pronuncia="".join(tokens[1:])
            g2plist.append((word,pronuncia))
        if fname!="-":
            fd.close()
        for (w,p) in g2plist:
            data="\\pronuncia{"+w+"}{"+self.defref+"}{"+p+"}"
            self.append(Pronuncia(data))

    def save_g2p(self,fname):
        if fname=="-":
            fd=sys.stdout
        else:
            if not os.path.exists(fname): return
            fd=open(fname,'w')
        for p in self:
            w=self.to_g2p(p.voce)
            r=list(p.pronuncia.decode())
            t=w+" "+u" ".join(r)+"\n"
            fd.write(t)
        if fname!="-":
            fd.close()

    def from_g2p(self,word):
        t=""
        print word
        for ch in word:
            t+=FROM_G2P_CONVERSIONI[ch]
        return(t)
        
    def to_g2p(self,word):
        t=""
        L=len(word)
        n=0
        while n<L:
            ch=word[n]
            add=1
            if ( (word[n] in [ ":",".","_","^" ])
                  or ( (n<L-1) and (word[n+1] in [ "T", "N" ]) ) ):
                ch=word[n:n+2]
                add=2
            t+=TO_G2P_CONVERSIONI[ch]
            n+=add
        return(t)
        
