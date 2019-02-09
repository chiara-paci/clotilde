# -*- coding: utf-8 -*-

from config import *
import os
import re
from Parola import Parola,ParSuffisso
from Voci import VoceOttomana,VOttVariante
import sys
from GRiga import GRiga
from GMatch           import GMatchSimil,GMatchRadice,GMatchPrefix

class Suddivisione(object):
    def __init__(self,parola,voce,base_suff):
        self.parola=parola
        self.voce=voce
        self.suffisso_base=base_suff
        self.suffissi=[]

class Suffisso(GRiga):
    def __init__(self,data):
        GRiga.__init__(self,data,3,"suffisso","Turco",baseclass=ParSuffisso)
        self.verificare=False
        self.noteverificare=""
        self.split_args()
        self.parole=[]
        self.mk_regexp()

    def mk_regexp(self):
        if self.allomorfi:
            base="|".join(self.allomorfi)
        else:
            base=self.parola.realword
        base=base.replace("^","\^")
        self.regexp='^('+base+')(.*)$'
        self.regexp_simil='^('+base+')$'
        self.re=re.compile(r''+self.regexp)
        self.re_simil=re.compile(r''+self.regexp_simil)

    def split_args(self):
        (self.classe,self.origine,self.categoria,
         self.voce,allomorfi,pfonte,self.pronuncia,
         self.input,self.output,self.significato,sfonte)=self.args
        self.references_pron=self.split_references(pfonte)
        self.references=self.split_references(sfonte)
        punt_re=re.compile(" +([.,;:])")
        self.allomorfi=filter(bool,allomorfi.split("/"))
        self.significato=punt_re.sub(r'\1',self.significato)
        if re.match(r'.*\\verificare.*',self.significato):
            self.verificare=True
            if re.match(r'.*\\verificare\[[^\[\]]+\]',self.significato):
                txt=re.findall(r'.*\\verificare\[([^\[\]]*)\].*',
                               self.significato)[0]
                self.noteverificare=txt
                self.significato=re.sub(r'\\verificare\[([^\[\]]*)\]',
                                        '',self.significato)
            else:
                self.significato=self.significato.replace('\\verificare','')
        self.significato=self.significato.strip()
        if not self.significato: return
        if self.significato[-1] in [",",":",".",";"]:
            self.significato=self.significato[:-1]
        self.significato=self.significato.strip()

    def save_item(self,fd,tipo=""):
        if not tipo: tipo=self.tipo
        sfonte=self.join_references(self.references)
        pfonte=self.join_references(self.references_pron)
        signif=self.significato
        allomorfi="/".join(self.allomorfi)
        if self.verificare:
            signif+=" \\verificare"
            if self.noteverificare:
                signif+="["+self.noteverificare+"]"
        args=[self.classe,self.origine,self.categoria,
              self.voce,allomorfi,pfonte,self.pronuncia,
              self.input,self.output,self.significato,sfonte]
        txt="\\suffisso"
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
        if self.classe:
            pron+=" ("+self.classe+")"
            virg=","
        if bullet:
            fd.write("\\item["+bullet+"] "+txt+virg+pron)
        else:
            fd.write("\\item["+txt+virg+"]"+pron)
        conv=[]
        if self.origine:
            fd.write(", "+self.origine.lower().strip()+".")
        if self.input:
            conv.append("si applica a "+TUTTE_CATEGORIE[self.input].lower())
        if self.output:
            conv.append("genera "+TUTTE_CATEGORIE[self.output].lower())
        if conv:
            fd.write("; "+", ".join(conv))
        if self.significato:
            fd.write("; "+self.significato.strip())
        fd.write("\n")
        fd.write("\\begin{subvocedue}\n")
        self.print_ref(fd,self.references_pron,
                       "Pron. ("+str(self.pron_valutazione())+")")
        self.print_ref(fd,self.references,"Rif.")
        fd.write("\\end{subvocedue}\n")

    def __eq__(self,other):
        if type(other) in [Parola,ParSuffisso]:
            return(self.parola.__eq__(other))
        if type(other) in [VoceOttomana,VOttVariante]:
            return(self.__eq__(other.parola))
        flag=self.parola.__eq__(other.parola)
        if not flag: return(False)
        return( (self.input==other.input)
                and (self.ouput==other.output) )

    def __ne__(self,other):
        if type(other) in [Parola,ParSuffisso]:
            return(self.parola.__ne__(other))
        if type(other) in [VoceOttomana,VOttVariante]:
            return(self.__ne__(other.parola))
        flag=self.parola.__eq__(other.parola)
        if not flag: return(True)
        return( (self.input!=other.input)
                or (self.ouput!=other.output) )

    def __lt__(self,other):
        if type(other) in [Parola,ParSuffisso]:
            return(self.parola.__lt__(other))
        if type(other) in [VoceOttomana,VOttVariante]:
            return(self.__lt__(other.parola))
        flag=self.parola.__eq__(other.parola)
        if not flag:
            return(self.parola.__lt__(other.parola))
        if self.input<other.input: return(True)
        if self.input>other.input: return(False)
        if self.output<other.output: return(True)
        return(False)
        
    def __gt__(self,other):
        if type(other) in [Parola,ParSuffisso]:
            return(self.parola.__gt__(other))
        if type(other) in [VoceOttomana,VOttVariante]:
            return(self.__gt__(other.parola))
        flag=self.parola.__eq__(other.parola)
        if not flag:
            return(self.parola.__gt__(other.parola))
        if self.input>other.input: return(True)
        if self.input<other.input: return(False)
        if self.output>other.output: return(True)
        return(False)

    def __le__(self,other):
        if type(other) in [Parola,ParSuffisso]:
            return(self.parola.__le__(other))
        if type(other) in [VoceOttomana,VOttVariante]:
            return(self.__le__(other.parola))
        flag=self.parola.__eq__(other.parola)
        if not flag:
            return(self.parola.__le__(other.parola))
        if self.input<other.input: return(True)
        if self.input>other.input: return(False)
        if self.output<other.output: return(True)
        if self.output>other.output: return(False)
        return(True)

    def __ge__(self,other):
        if type(other) in [Parola,ParSuffisso]:
            return(self.parola.__ge__(other))
        if type(other) in [VoceOttomana,VOttVariante]:
            return(self.__ge__(other.parola))
        flag=self.parola.__eq__(other.parola)
        if not flag:
            return(self.parola.__ge__(other.parola))
        if self.input>other.input: return(True)
        if self.input<other.input: return(False)
        if self.output>other.output: return(True)
        if self.output<other.output: return(False)
        return(True)

    def simil(self,other):
        if type(other) in [Parola,ParSuffisso]:
            return(self.parola.simil(other))
        if type(other) in [VoceOttomana,VOttVariante]:
            return(self.simil(other.parola))
        w=other.parola.word.replace("|","").replace("-","")
        if self.re_simil.match(w): return(1.0)
        return(self.parola.simil(other.parola))

    def split(self,parsuffisso):
        w=parsuffisso.realword.replace("|","").replace("-","")
        x=self.re.findall(w)
        if not x: return('')
        t=x[0]
        if len(t)==1: return('')
        s=t[-1]
        if not s: return('')
        #if s[0]=="N":
        #    print word,x,'^('+self.regexp+')(.*)$'
        return(s)

    def is_prefix(self,parsuffisso):
        w=parsuffisso.realword.replace("|","").replace("-","")
        return(self.re.match(w))

class Suffissi(list):
    def __init__(self,finput):
        self.finput=finput
        self.glossario=None
        self.divisioni=None
        list.__init__(self)

    def save(self,fd):
        fd.write("% suffissi\n")
        fd.write("\n")
        for voce in self:
            voce.save_item(fd)

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
        righekeys=[ "suffisso" ]
        tipo_re=re.compile("^.([^{[ ]*)[{[].*")
        cont_re=re.compile("^ .*")
        comm_re=re.compile("%.*")
        currenttxt=""
        for row in fd.readlines(): 
            r=row.replace("\n","").strip()
            if ( (not r) or (comm_re.match(r)) ):
                if currenttxt:
                    s=Suffisso(currenttxt)
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
                    s=Suffisso(currenttxt)
                    self.append(s)
                currenttxt=""
                continue
            if currenttxt:
                s=Suffisso(currenttxt)
                self.append(s)
            currenttxt=r
        if currenttxt:
            s=Suffisso(currenttxt)
            self.append(s)
        if self.finput!="-":
            fd.close()
        self.sort()

    def match(self,suff,parsuffisso):
        sim=suff.simil(parsuffisso)
        if sim>=0.5:
            return( GMatchSimil(sim) )
        if suff.is_prefix(parsuffisso):
            s=suff.split(parsuffisso)
            print "Y",suff.parola.word,suff.allomorfi,suff.regexp,parsuffisso.word,s
            print "D",suff.parola.word,suff.allomorfi,suff.regexp_simil,parsuffisso.word
            psuff=ParSuffisso(s)
            psuff.parole=map(lambda x:x,parsuffisso.parole)
            return( GMatchPrefix(len(suff.parola),psuff) )
        return(None)

    def get_all(self):
        tutti=map(lambda x: x,self)
        tutti+=map(lambda x: x, self.solo_doc)
        tutti.sort()
        return(tutti)

    def add_glossario(self,glossario):
        self.glossario=glossario
        self.calcola_suffissi()
        #self.calcola_divisioni()

    def get_divisioni(self):
        divisioni=[]
        for v in self.glossario.get_all():
            vdiv=v.get_divisioni()
            map(lambda x: divisioni.append([x[0],v,x[1]]),vdiv)
        new_divisioni={}
        for (parola,voce,suffisso) in divisioni:
            if not new_divisioni.has_key(suffisso):
                new_divisioni[suffisso]=[]
            new_divisioni[suffisso].append( (parola,voce))
        divisioni=[]
        for (s,L) in new_divisioni.items():
            if not s:
                divisioni.append(['',[],L])
            elif self.predivisioni.has_key(s):
                divisioni.append([s,self.predivisioni[s],L])
            else:
                divisioni.append([s,[s],L])
        return(divisioni)
    
    def calcola_suffissi(self):
        new_suffissi=[]
        for v in self.glossario.get_all():
            vsuff=v.get_suffissi()
            for p in vsuff:
                if p not in new_suffissi:
                    new_suffissi.append(p)
                else:
                    ind=new_suffissi.index(p)
                    for par in p.parole:
                        if not par in new_suffissi[ind].parole:
                            new_suffissi[ind].parole.append(par)

        continua=True
        while continua:
            suffissi=map(lambda x:x,new_suffissi)
            par_matches={}
            for suff in self:
                par=[]
                for parsuffisso in suffissi:
                    m=self.match(suff,parsuffisso)
                    if not m: continue
                    par.append( (m,parsuffisso) )
                    if not par_matches.has_key(parsuffisso):
                        par_matches[parsuffisso]=[]
                    par_matches[parsuffisso].append( (m,suff) )
                    if parsuffisso in new_suffissi:
                        new_suffissi.remove(parsuffisso)
                if par:
                    suff.matches+=par

                continua=bool(par_matches)
                # test sui tipi di match e poi rigirare tutto
                
                for (parsuffisso,vlist) in par_matches.items():
                    if len(vlist)<=1: continue
                    vlist.sort()
                    vlist.reverse()
                    primo=vlist[0]
                    m=primo[0]
                    if type(m)==GMatchPrefix:
                        if m.altro not in new_suffissi:
                            #print "NEW",m.altro.word
                            new_suffissi.append(m.altro)
                        else:
                            ind=new_suffissi.index(m.altro)
                            for mapar in m.altro.parole:
                                if mapar not in new_suffissi[ind].parole:
                                    new_suffissi[ind].parole.append(mapar)
                            #print "OLD",m.altro.word,new_suffissi[ind].word
                    for v in vlist[1:]:
                        if not ( primo[1]==v[1] ):
                            if (v[0],parsuffisso) in v[1].matches:
                                v[1].matches.remove((v[0],parsuffisso))

        self.solo_doc=new_suffissi
        #self.solo_doc.sort()

    def load_predivisioni(self,divisioni):
        self.f_divisioni=divisioni
        if self.f_divisioni=="-":
            fd=sys.stdin
        else:
            if not os.path.exists(self.f_divisioni): return
            fd=open(self.f_divisioni,'r')
        self.predivisioni={}
        comm_re=re.compile("%.*")
        for row in fd.readlines():
            r=row.replace("\n","").strip()
            if ( (not r) or (comm_re.match(r)) ): continue
            tokens=r.split("@")
            suff=tokens[0]
            if len(tokens)>1:
                divisioni=tokens[1].split("/")
            else:
                divisioni=[]
            if len(tokens)>2:
                varianti=tokens[2].split("/")
            else:
                varianti=[]
            self.predivisioni[suff]=tokens[1:]
        if self.f_divisioni!="-":
            fd.close()
        
    def save_predivisioni(self,fd):
        fd.write("% divisioni\n")
        fd.write("\n")
        for (s,tokens) in self.predivisioni.items():
            r=s+"@"+"@".join(tokens)
            fd.write(r+"\n")
        

        
