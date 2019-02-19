# -*- coding: utf-8 -*-

from config import *
import re
import sys

#from Voci import VoceOttomana,VOttVariante
#from Suffissi import Suffisso

class Parola(object):
    def __init__(self,word,sezione):
        self.word=word
        self.sezione=sezione
        self.righe={}
        self.setverb=False
        self.realword=self.word
        self.calcola_flags()
        self.calcola_order_hash()

    def get_cardinalita(self):
        C=0
        for r in self.righe.values():
            C+=len(r)
        return(C)

    def calcola_flags(self):
        flags=re.compile("^{.setverb (.*)}$")
        if not flags.match(self.word):
            return
        w=flags.findall(self.word)
        self.setverb=True
        self.realword=w[0].strip()

    def calcola_sostegno_hamza(self,n,onlyadd=True):
        if n==0: return("A")
        if n==1:
            prec=self.realword[0]
        elif self.realword[n-2] in SWITCHES:
            prec=self.realword[n-2:n]
        else:
            prec=self.realword[n-1]
        if self.realword[n]!="'":
            if onlyadd: return("")
            if prec in LETTERE_TUTTE: return(prec)
            return("B")
        if n==len(self.realword)-1:
            succ=""
        elif n==len(self.realword)-2:
            succ=self.realword[len(self.realword)-1]
        elif self.realword[n+1] in SWITCHES:
            succ=self.realword[n+1:n+3]
        else:
            succ=self.realword[n+1]
        if self.setverb:
            if onlyadd: return("")
            if succ in LETTERE_TUTTE: return(succ)
            return("B")
        if ( (prec in HARAKAT[HARAKAT_IND["i"]])
             or (succ in HARAKAT[HARAKAT_IND["i"]]) ): return("y")
        if ( (prec in HARAKAT[HARAKAT_IND["u"]])
             or (succ in HARAKAT[HARAKAT_IND["u"]]) ): return("w")
        return("A")

    def calcola_order_hash(self):

        def o_status(n,ch,caratteri):
            h_ret=[]
            c_ret=[]
            l_ret=[]

            if ch in IGNORA:
                return( (c_ret,h_ret,l_ret))

            if ( (n!=0) and (ch not in HARAKAT_TUTTE) ):
                if ( (caratteri)
                     and (caratteri[-1] not in HARAKAT_TUTTE+VOCALI_LUNGHE)
                     and (ch not in VOCALI_LUNGHE) ):
                    h_ret.append(ORDER_HARAKAT["sukun"])
                    c_ret=["sukun"]

            if ch in HAMZA:
                sost=self.calcola_sostegno_hamza(n)
                if not sost:
                    return( (c_ret,h_ret,l_ret))
                (c,h_ret,l_ret)=o_status(n,sost,caratteri)
                c_ret.append(sost)
                return( (c_ret,h_ret,l_ret))

            if ( (n==0) and (ch in MULTIPLE_INIZIO.keys()) ):
                for newch in MULTIPLE_INIZIO[ch]:
                    (c,h,l)=o_status(n,newch,caratteri)
                    h_ret+=h
                    l_ret+=l
                c_ret.append(ch)
                return( (c_ret,h_ret,l_ret))
                    
            if ch in MULTIPLE.keys():
                for newch in MULTIPLE[ch]:
                    (c,h,l)=o_status(n,newch,caratteri)
                    h_ret+=h
                    l_ret+=l
                c_ret.append(ch)
                return( (c_ret,h_ret,l_ret))
            
            if ch not in HARAKAT_TUTTE:
                c_ret.append(ch)
                l_ret.append(ORDER_LETTERE[ch])
                return( (c_ret,h_ret,l_ret))

            if n==0:
                l_ret.append(ORDER_LETTERE["A"])
            elif ( (self.realword[n-1] in [ "-" ])
                   and not ( (ch=="i") and (n==len(self.realword)-1) ) ):
                l_ret.append(ORDER_LETTERE["A"])
            h_ret.append(ORDER_HARAKAT[ch])
            c_ret.append(ch)
            return( (c_ret,h_ret,l_ret))

        n=0
        o_lettere=[]
        o_harakat=[]
        caratteri=[]
        while n<len(self.realword):
            ch=self.realword[n]
            if ch=="\\":
                if self.realword[n+1:n+10]=="mancantef":
                    o_lettere+=[ORDER_LETTERE["y"],ORDER_LETTERE["y"],
                                ORDER_LETTERE["y"]]
                    n+=10
                    continue
            if ch=="(":
                while self.realword[n]!=")":
                    n+=1
                n+=1
                continue

            add=0
            if ch in SWITCHES:
                ch+=self.realword[n+add+1]
                add+=1

            if ( (ch in HARAKAT_TUTTE) 
                 and (n+add<(len(self.realword)-1))
                 and (self.realword[n+add+1]==NUN_SIGN) ):
                ch+=self.realword[n+add+1]
                add+=1

            (c_add,h_add,l_add)=o_status(n,ch,caratteri)
            o_lettere+=l_add
            o_harakat+=h_add
            oldn=n
            n+=(1+add)
            if not c_add: continue
            caratteri+=c_add[:-1]
            ch=c_add[-1]
            if ( (n>=len(self.realword)) and (self.realword[oldn-1]=="-") ):
                caratteri.append("-"+ch)
                continue
            caratteri.append(ch)

        self.order_lettere=tuple(o_lettere)
        self.order_harakat=tuple(o_harakat)
        self.caratteri=caratteri

    def get_primo_carattere(self):
        if self.caratteri:
            return(self.caratteri[0])
        return("-")

    def __len__(self): return(len(self.order_lettere))

    def add_pos(self,riga,pos):
        if not self.righe.has_key(riga):
            self.righe[riga]=[]
        self.righe[riga].append(pos)

    def print_parole(self,fd):
        T="\\item ("+self.sezione+") "+spzrl(self.word)+":"
        #if self.word[0]!="{":
        #    T="\\item ("+self.sezione+") \\spzrl{"+self.word+"}:"
        #else:
        #    T="\\item ("+self.sezione+") \\spzrl"+self.word+":"
        R=map(int,self.righe.keys())
        R.sort()
        for riga in R:
            T+=" "+str(riga+1)+" ("+",".join(map(str,self.righe[riga]))+")"
        T+="\n"
        fd.write(T)

    def print_simil(self,ind=0.0,primo=False):
        if primo:
            pref= "+ "
            priga="  R: "
        else:
            pref= "  = ("+str(ind)+":"+self.caratteri[-1]+") "
            priga="    R: "
        print pref+self.word
        R=map(int,self.righe.keys())
        R.sort()
        for riga in R:
            T=priga+str(riga+1)+" ("+",".join(map(str,self.righe[riga]))+")"
            print T

    def print_csv(self,fd):
        T=self.sezione+"@"+self.word
        R=map(int,self.righe.keys())
        R.sort()
        for riga in R:
            T+="@"+str(riga+1)+":"+",".join(map(str,self.righe[riga]))
        T+="\n"
        fd.write(T)

    def print_row(self,fd,bullet="",color=""):
        word_label=spzrl(self.word)
        #if self.word[0]=="{":
        #    word_label="\\spzrl"+self.word
        #else:
        #    word_label="\\spzrl{"+self.word+"}"
        
        if color:
            bullet="{\\color{"+color+"}"+bullet+"}"
            txt="{\\color{"+color+"}"+word_label+"}"
        else:
            txt=word_label
        fd.write(bullet+"&"+txt+"\\\\\n")

    def print_item(self,fd,suffissi=[],bullet="",color=""):
        word_label=spzrl(self.word)

        #if self.word[0]=="{":
        #    word_label="\\spzrl"+self.word
        #else:
        #    word_label="\\spzrl{"+self.word+"}"
        
        if color:
            bullet="{\\color{"+color+"}"+bullet+"}"
            txt="{\\color{"+color+"}"+word_label+"}"
        else:
            txt=word_label
        if bullet:
            fd.write("\\item["+bullet+"] "+txt+" ")
        else:
            fd.write("\\item["+txt+"] ")
        if suffissi:
            T="("+",".join(map(spzrl,map(str,suffissi)))+") "
            fd.write(T)
        T=""
        R=map(int,self.righe.keys())
        R.sort()
        for riga in R:
            T+=" "+str(riga+1)+" ("+",".join(map(str,self.righe[riga]))+")"
        T+="\n"
        fd.write(T)

    def righe_to_str(self):
        R=map(int,self.righe.keys())
        R.sort()
        tlista=[]
        for riga in R:
            tlista.append(str(riga+1)+" ("+",".join(map(str,self.righe[riga]))+")")
        return(" ".join(tlista))

    def __str__(self):
        return(self.sezione+" "+self.word+" "+str(self.righe))

    def __gt__(self,other):
        if self.sezione!=other.sezione:
            s_ind=SEZIONI.index(self.sezione)
            o_ind=SEZIONI.index(other.sezione)
            return(s_ind > o_ind)

        if self.order_lettere > other.order_lettere: return(True)
        if self.order_lettere < other.order_lettere: return(False)
        return(self.order_harakat>other.order_harakat)

    def __lt__(self,other): 
        if self.__eq__(other): return(False)
        return(not self.__gt__(other))

    def __le__(self,other):
        if self.__eq__(other): return(True)
        return(self.__lt__(other))

    def __ge__(self,other): 
        if self.__eq__(other): return(True)
        return(self.__gt__(other))
    
    def __ne__(self,other):
        if not other: return(False)
        return(not self.__eq__(other))

    def __eq__(self,other):
        if self.sezione!=other.sezione: return(False)
        uguali=( (self.order_lettere==other.order_lettere)
                 and (self.order_harakat==other.order_harakat) )
        if not uguali: return(False)
        if ( (self.word[-1]=="B") and (other.word[-1]!="B") ): return(False)
        if ( (self.word[-1]!="B") and (other.word[-1]=="B") ): return(False)
        return(True)

    def simil(self,other):
        #if self.realword=="in||-^s'BA||-al-lah":
        #    print "S:", self.order_lettere
        #    print "O:", other.order_lettere
        #    print
        ind=0
        if self.order_lettere!=other.order_lettere:
            return(0.0)
        if self.__eq__(other): return(1)
        ind+=0.5
        lista=[ "^a", "-i" ]
        if ( (self.caratteri[-1] in lista)
             and (other.caratteri[-1] in lista ) ):
            return(1)
        if self.caratteri[-1] in lista:
            return(ind)
        if other.caratteri[-1] in lista:
            return(ind)
        return(1.0)

class ParSuffisso(Parola):
    def __init__(self,word):
        Parola.__init__(self,word,"Turco")
        self.parole=[]

    def __getattribute__(self,name):
        if name!="righe": return(Parola.__getattribute__(self,name))
        righe={}
        for p in self.parole:
            for (r,ind) in p.righe.items():
                if not righe.has_key(r): righe[r]=[]
                righe[r]+=ind
        return(righe)

    def add_le_parole_di(self,other):
        self.parole+=other.parole
