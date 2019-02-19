# -*- coding: utf-8 -*-

from config import *

from GtkUtility import get_conversione,VTRASCRIZIONE

import re

class Riga(object):
    def __init__(self,numero,tipo,num_args,data):
        self.data=data
        self.tipo=tipo
        self.num_args=num_args
        self.numero=numero
        Q="^.itemtesto"+self.tipo+"{([^}]+)}{([^}]+)}(.*)"
        p=re.compile(Q)
        t=p.findall(self.data)
        self.scale=t[0][0]
        self.image=t[0][1]
        self.text=t[0][2]
        self.args=[]
        self.estrai_args()

    def estrai_args(self):
        aperte=re.compile("{")
        chiuse=re.compile("}")
        status="inizio"
        txt=""
        for ch in self.text:
            if status=="inizio":
                if ch!="{": continue
                status="arg"
                continue
            if ch!="}":
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

    def trascrivi(self,txt):
        no=re.compile(".LR{.tref{a[0-9]}}")
        txt=no.sub("",txt)
        sre=re.compile("  *")
        txt=sre.sub(" ",txt)
        
        #S="("+txt+")\n"
        S=""
        S+=get_conversione(txt,VTRASCRIZIONE)
        return(S)

    def trascrizione(self,fd):
        fd.write("\n")
        #fd.write(str(self.numero)+" "+self.tipo+" "+str(len(self.args))+"\n")
        fd.write(str(self.numero)+"\n")

        S=self.trascrivi(self.args[0].strip())
        fd.write(S+"\n")

        if self.tipo!="araboturco": return

        T=self.trascrivi(self.args[1].strip())
        fd.write(T+"\n")

    def __str__(self):
        T="\\itemtesto"+self.tipo
        T+="{"+self.scale+"}"
        T+="{"+self.image+"}"
        T+=''.join(map(lambda x: "{"+x+"}",self.args))
        return(T)

    def parole(self):
        tok=self.parsing(self.args[0])
        if self.tipo=="arabo":
            tok=map(lambda x: ("Arabo",x),tok)
            return(tok)
        if self.tipo=="turco":
            tok=map(lambda x: ("Turco",x),tok)
            return(tok)
        toka=map(lambda x: ("Arabo",x),tok)
        tok=self.parsing(self.args[1])
        tokt=map(lambda x: ("Turco",x),tok)
        return(toka+tokt)
        
    def parsing(self,text):
        txt=""
        status="inizio"
        tokens=[]
        aperte=re.compile("{")
        chiuse=re.compile("}")
        for ch in text:
            if status=="inizio":
                if ch in ["\n"," ","\t"]: continue
                if ch=="{":
                    txt=ch
                    status="tokenpar"
                    continue
                if ch=="\\":
                    txt=ch
                    status="tokencmd"
                    continue
                txt=ch
                status="token"
                continue
            if status=="tokenpar":
                txt+=ch
                if ch!="}":
                    continue
                num_aperte=len(aperte.findall(txt))
                num_chiuse=len(chiuse.findall(txt))
                if num_aperte==num_chiuse:
                    tokens.append(txt)
                    txt=""
                    status="inizio"
                    continue
                continue
            if status=="token":
                if ch in ["\n"," ","\t"]:
                    tokens.append(txt)
                    txt=""
                    status="inizio"
                    continue
                if ch=="\\":
                    tokens.append(txt)
                    txt=ch
                    status="tokencmd"
                    continue
                txt+=ch
                continue
            if ch=="{":
                txt+=ch
                status="tokenpar"
                continue
            if ch in ["\n"," ","\t"]:
                tokens.append(txt)
                txt=""
                status="inizio"
                continue
            txt+=ch
        if status=="inizio":
            return(tokens)
        tokens.append(txt)
        return(tokens)
