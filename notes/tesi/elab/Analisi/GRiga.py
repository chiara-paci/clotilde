# -*- coding: utf-8 -*-

from config import *
import os
import re
from Parola import Parola,ParSuffisso
import sys

class TexRiga(object):
    def __init__(self,data,tipo):
        self.data=data
        self.tipo=tipo
        Q="^."+self.tipo
        self.text=re.sub(Q,"",self.data)
        self.args=[]
        self.fac_args=[]
        self.estrai_args()

    def estrai_args(self):
        aperte=re.compile("{")
        chiuse=re.compile("}")
        qaperte=re.compile("\[")
        qchiuse=re.compile("\]")
        status="inizio"
        txt=""
        for ch in self.text:
            if status=="inizio":
                if ch not in [ "{", "[" ]: continue
                if ch=="[":
                    status="fac"
                    continue
                status="arg"
                continue
            if status=="fac":
                if ch != "]":
                    txt+=ch
                    continue
                num_aperte=len(qaperte.findall(txt))
                num_chiuse=len(qchiuse.findall(txt))
                if num_aperte==num_chiuse:
                    self.fac_args.append(txt)
                    txt=""
                    status="inizio"
                    continue
                txt+=ch
                continue
            if ch != "}":
                txt+=ch
                continue
            num_aperte=len(aperte.findall(txt))
            num_chiuse=len(chiuse.findall(txt))
            if num_aperte==num_chiuse:
                self.args.append(txt)
                txt=""
                status="inizio"
                continue
            txt+=ch

class GRiga(TexRiga):
    def __init__(self,data,voceind,tipo,sezione,baseclass=Parola):
        #self.data=data
        #self.tipo=tipo
        TexRiga.__init__(self,data,tipo)
        if baseclass==Parola:
            self.parola=Parola(self.args[voceind],sezione)
        else:
            self.parola=baseclass(self.args[voceind])
        self.matches=[]

    def __getattribute__(self,name):
        if name in [ "sezione", "order_lettere", "order_harakat", "word" ]:
            return(self.parola.__getattribute__(name))
        return(object.__getattribute__(self,name))

    def get_primo_carattere(self): return(self.parola.get_primo_carattere())

    def is_verbo(self): return(False)

    def __len__(self): return(len(self.parola))

    def __str__(self):
        T=" ".join(self.args)
        return(T)


    def __hash__(self): return(id(self))

    def __eq__(self,other):
        if type(other) in [Parola,ParSuffisso]:
            return(self.parola.__eq__(other))
        return(self.parola.__eq__(other.parola))

    def __ne__(self,other):
        if type(other) in [Parola,ParSuffisso]:
            return(self.parola.__ne__(other))
        return(self.parola.__ne__(other.parola))

    def __lt__(self,other):
        if type(other) in [Parola,ParSuffisso]:
            return(self.parola.__lt__(other))
        return(self.parola.__lt__(other.parola))

    def __gt__(self,other):
        if type(other) in [Parola,ParSuffisso]:
            return(self.parola.__gt__(other))
        return(self.parola.__gt__(other.parola))

    def __le__(self,other):
        if type(other) in [Parola,ParSuffisso]:
            return(self.parola.__le__(other))
        return(self.parola.__le__(other.parola))

    def __ge__(self,other):
        if type(other) in [Parola,ParSuffisso]:
            return(self.parola.__ge__(other))
        return(self.parola.__ge__(other.parola))

    def simil(self,other):
        if type(other) in [Parola,ParSuffisso]:
            return(self.parola.simil(other))
        return(self.parola.simil(other.parola))

    def print_item(self,fd,bullet=""): pass

    def join_references(self,lista):
        slista=[]
        for (k,L) in lista.items():
            map(lambda x: slista.append(k+"/"+"/".join(x)),L)
        return(";".join(slista))

    def split_references(self,data):
        ret={}
        for pref in data.split(";"):
            r=pref.split("/")
            if len(r)<=1: continue
            if not ret.has_key(r[0]):
                ret[r[0]]=[]
            ret[r[0]].append(r[1:])
        return(ret)

    def print_ref(self,fd,lista,prefix):
        if not lista: return
        def map_bib(B):
            T="\\spzcite"
            if len(B)>1: T+="["+B[1]+"]"
            T+="{"+B[0]+"}"
            return(T)
        def map_sec(B):
            T="\\sezione"
            if len(B)>1: T+="["+B[1]+"]"
            T+="{"+B[0]+"}"
            return(T)
        def map_tab(B):
            T="\\tabella"
            if len(B)>1: T+="["+B[1]+"]"
            T+="{"+B[0]+"}"
            return(T)
        fmap={"bib": map_bib, "sec": map_sec, "tab": map_tab}
        if lista:
            fd.write("\\item["+prefix+":] ")
            L=[]
            for k in [ "sec", "bib", "tab" ]:
                if lista.has_key(k):
                    L+=map(fmap[k],lista[k])
            txt=", ".join(L)
            fd.write(txt+"\n")

