# -*- coding: utf-8 -*-

from config import *
import re

from GRiga import TexRiga

class IdxBase(object):
    def __init__(self,entry,lingua,modificatore):
        self.entry=entry
        self.cod_lingua=lingua
        self.modificatore=modificatore
        if lingua in [ "ar","per" ]:
            self.texentry=spzrl(self.entry)
        elif lingua in [ "gr", "biz" ]:
            self.texentry="\\textgreek{"+self.entry+"}"
        elif lingua=="ott":
            a=self.entry.split("/")
            self.texentry=spzrl(a[0])+",~"+"\\spzpr{"+a[1]+"}"
        else:
            self.texentry=self.entry

    def __eq__(self,other):
        return( (self.cod_lingua==other.cod_lingua)
                and (self.entry==other.entry) )

    def __ne__(self,other):
        return(not self.__eq__(other))

    def __lt__(self,other):
        if self.__eq__(other): return(False)
        if self.cod_lingua!=other.cod_lingua:
            return(self.cod_lingua<other.cod_lingua)
        return(self.entry<other.entry)

    def __le__(self,other):
        if self.__eq__(other): return(True)
        return(self.__lt__(other))
    
    def __gt__(self,other): return(other.__lt__(self))
    def __ge__(self,other): return(other.__le__(self))

    def __str__(self):
        S=self.cod_lingua+":"+self.entry
        return(S)

class IndexEntry(TexRiga,IdxBase):
    def __init__(self,data):
        TexRiga.__init__(self,data,"indexentry")
        self.pagina=self.args[1]
        t=self.args[0].split("|")
        self.hyperpage=bool((len(t)==2) and (t[1]=="hyperpage"))
        entry=self.pulisci(t[0])
        t=entry.split("/")
        cod_lingua=t[0]
        if len(t)==3: modificatore=t[2]
        else: modificatore=""
        t=t[1].split("!")
        entry=t[0]
        IdxBase.__init__(self,entry,cod_lingua,modificatore)
        if len(t)>1:
            self.subentry=t[1:]
        else:
            self.subentry=[]

    def pulisci(self,txt):
        for (trova,rep) in [ ("\IeC {\c c}","ç") ]:
            txt=txt.replace(trova,rep)
        return(txt)

    def __str__(self):
        S=IdxBase.__str__(self)
        if self.subentry:
            S+=" "+str(self.subentry)
        S+=" "+str(self.pagina)
        return(S)

class IndexItem(IdxBase):
    def __init__(self,obj):
        self.pagine=[]
        self.subentries=[]
        if type(obj)==IndexEntry:
            (entry,cod_lingua,modificatore,
             pagina,subentry)=(obj.entry,obj.cod_lingua,obj.modificatore,
                               obj.pagina,obj.subentry)
        else:
            (entry,cod_lingua,modificatore,pagina,subentry)=obj
        if subentry:
            IdxBase.__init__(self,entry,cod_lingua,"")
            self.subentries.append( IndexItem( (subentry[0],cod_lingua,modificatore,
                                                pagina,subentry[1:])) )
        else:
            IdxBase.__init__(self,entry,cod_lingua,modificatore)
            self.pagine.append(pagina)

    def merge(self,other):
        s=set(self.pagine+other.pagine)
        self.pagine=list(s)

        for sub in other.subentries:
            if sub not in self.subentries:
                self.subentries.append(sub)
                continue
            ind=self.subentries.index(sub)
            self.subentries[ind].merge(sub)

    def to_tex(self,fd):
        if self.modificatore=="fs":
            fd.write("\\item[\\formasupposta{"+self.texentry+"}]")
        else:
            fd.write("\\item["+self.texentry+"]")
        if self.pagine:
            fd.write(" "+", ".join(map(lambda x: "\\hyperpage{"+x+"}",
                                       self.pagine)))
        else:
            fd.write("\mbox{ }")
        fd.write("\n")
        if self.subentries:
            fd.write("\\begin{subglotermini}\n")
            for it in self.subentries:
                it.to_tex(fd)
            fd.write("\\end{subglotermini}\n")

class Lingua(list):
    def __init__(self,cod_label):
        self.cod_label=cod_label
        if LINGUE.has_key(self.cod_label):
            self.lingua=LINGUE[self.cod_label]
        else:
            print "No",self.cod_label
            self.lingua="Boh ("+self.cod_label+")"
        list.__init__(self)

    def __eq__(self,other):
        return(self.cod_label==other.cod_label)

    def __ne__(self,other): return(not self.__eq__(other))

    def __lt__(self,other):
        if self.lingua==other.lingua:
            return(self.cod_label<other.cod_label)
        return(self.lingua<other.lingua)
        
    def __le__(self,other):
        if self.__eq__(other): return(True)
        return(self.__lt__(other))
    
    def __gt__(self,other): return(other.__lt__(self))
    def __ge__(self,other): return(other.__le__(self))

    def append(self,obj):
        if type(obj) not in [ IndexEntry, IndexItem ]: return

        if type(obj)==IndexItem:
            newobj=obj
        else:
            newobj=IndexItem(obj)

        #print newobj
        if newobj not in self:
            #print "A"
            list.append(self,newobj)
            return
        ind=self.index(newobj)
        #print "B", self[ind]
        self[ind].merge(newobj)

    def to_tex(self,fd):
        fd.write("\\begin{glotermini}{"+self.lingua+"}\n")
        self.sort()
        #fd.write("\\section{"+self.lingua+"}\n")
        #fd.write("\\begin{description}\n")
        for it in self:
            it.to_tex(fd)
        fd.write("\\end{glotermini}\n\n")

class Indice(object):
    def __init__(self,fdin,fdout):
        self.fdin=fdin
        self.fdout=fdout
        self.lingue={}

    def run(self):
        comm_re=re.compile("%.*")
        for row in self.fdin.readlines():
            r=row.replace("\n","").strip()
            if ( (not r) or (comm_re.match(r)) ):
                continue
            ie=IndexEntry(r)
            if not self.lingue.has_key(ie.cod_lingua):
                self.lingue[ie.cod_lingua]=Lingua(ie.cod_lingua)
            self.lingue[ie.cod_lingua].append(ie)

        L=self.lingue.values()
        L.sort()
        for lin in L:
            lin.to_tex(self.fdout)
