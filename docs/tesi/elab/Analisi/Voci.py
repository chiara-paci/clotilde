# -*- coding: utf-8 -*-

from config import *
import os
import re
from Parola import Parola,ParSuffisso
import sys

from GRiga import GRiga
from GMatch           import GMatchSimil,GMatchRadice

class VoceAraba(GRiga):
    def __init__(self,data):
        GRiga.__init__(self,data,0,"vocearaba","Arabo")
        ( self.voce,self.radice,
          self.significato_base,self.significato,sfonte )=self.args
        self.references=self.split_references(sfonte)

    def save_item(self,fd):
        args=[self.voce,self.radice,
              self.significato_base,
              self.significato]
        sfonte=self.join_references(self.references)
        args.append(sfonte)
        txt="\\vocearaba{"+"}{".join(args)+"}\n"
        fd.write(txt)

    def print_item(self,fd,bullet="",color=""):
        if not DRAFT and color=="colorsologlossario": return
        if color and DRAFT:
            if bullet: bullet="{\\color{"+color+"}"+bullet+"}"
            txt="{\\color{"+color+"}"+spzrl(self.radice.strip())+"}"
        else:
            txt=spzrl(self.radice.strip())
        if bullet and DRAFT:
            fd.write("\\item["+bullet+"] "+txt)
        else:
            fd.write("\\item["+txt+",]")
        fd.write(" "+self.significato_base.strip()+"\n")
        self.print_references(fd)
        fd.write("\\begin{subvocedue}\n")
        vtxt=spzrl(self.voce.strip())
        fd.write("\\item[\\subglossariobullet] "+vtxt)
        #fd.write("\\item["+vtxt+"]")
        fd.write(" "+self.significato.strip()+"\n")
        fd.write("\\end{subvocedue}\n")

    def print_references(self,fd):
        if not self.references: return
        fd.write("\\begin{subvocedue}\n")
        self.print_ref(fd,self.references,"Rif.")
        fd.write("\\end{subvocedue}\n")


class TRiga(GRiga):
    def __init__(self,data,voceind,tipo,sezione):
        self.references={}
        self.references_pron={}
        GRiga.__init__(self,data,voceind,tipo,sezione)
        self.split_args()
        self.mk_regexp()

    
    def print_references(self,fd):
        if not ( self.references or self.references_pron ): return
        fd.write("\\begin{subvocedue}\n")
        self.print_ref(fd,self.references_pron,
                       "Pron. ("+str(self.pron_valutazione())+")")
        self.print_ref(fd,self.references,"Rif.")
        fd.write("\\end{subvocedue}\n")

    def is_verbo(self): return(self.parola.word[-1]=="B")

    def split_args(self):
        ( self.occasione,self.voce,pfonte,self.pronuncia,sfonte )=self.args
        if self.fac_args:
            self.cosa_guardare=self.fac_args[0]
        else:
            self.cosa_guardare=""
        self.references_pron=self.split_references(pfonte)
        self.references=self.split_references(sfonte)

    def pron_valutazione(self):
        if not self.references_pron:
            return(0.0)
        else:
            return(1.0)

    def mk_regexp(self):
        base=self.parola.realword
        if base[-1]=="B":
            base=self.parola.realword[:-1]
        base=base.replace("^","\^").replace("|","\|")
        aprefix="(\^?A|:[AcCG]|a)"
        iprefix="(\^j|i)"
        tsuffix="([aeA]?[:_.]?[HT]|[aeA]t)"
        if (self.parola.realword[0]=="A"):
            base=aprefix+base[1:]
        elif ( (self.parola.realword[0]==":")
               and (self.parola.realword[1] in [ "A","c","C","G" ] ) ):
            base=aprefix+base[2:]
        elif ( (self.parola.realword[0]=="^")
               and (self.parola.realword[1] in [ "A" ] ) ):
            base=aprefix+base[2:]
        elif (self.parola.realword[0]=="i"):
            base=iprefix+base[1:]
        elif ( (self.parola.realword[0]=="^")
               and (self.parola.realword[1] in [ "j" ] ) ):
            base=iprefix+base[2:]
        if base[-1] in [ "T", "H" ]:
            n=-1
            if base[n-1] in [":","_","."]: n-=1
            if base[n-1] in ["a","e","A"]: n-=1
            base=base[:n]+tsuffix
        elif base[-1] in [ "t" ] and base[-2] in ["a","e","A"]:
            base=base[:-2]+tsuffix
        self.regexp=base
        self.re=re.compile(r'^'+self.regexp)
        self.resuff=re.compile(r'^('+self.regexp+')(.*)$')

    def is_radice(self,parola):
        R=self.re.match(parola.realword)
        return(R)

    def dividi_suffisso(self,word):
        x=self.resuff.findall(word)
        if not x: return('')
        t=x[0]
        if len(t)==1: return('')
        s=t[-1]
        if not s: return('')
        if s[0]=="N":
            print word,x,'^('+self.regexp+')(.*)$'
        return(s)

    def get_suffissi(self):
        suff=[]
        for (match,par) in self.matches:
            if type(match)==GMatchSimil: continue
            s=self.dividi_suffisso(par.realword)
            if not s: continue
            p=ParSuffisso(s)
            if p not in suff:
                suff.append(p)
            else:
                ind=suff.index(p)
                p=suff[ind]
            p.parole.append(par)
        return(suff)

    def get_divisioni(self):
        divisioni=[]
        for (match,par) in self.matches:
            if type(match)==GMatchSimil:
                divisioni.append((par,''))
                continue
            s=self.dividi_suffisso(par.realword)
            if not s:
                divisioni.append((par,''))
                continue
            divisioni.append((par,s))
        return(divisioni)

    def len_radice(self,parola):
        if self.is_radice(parola):
            maxlen=len(self)
        else:
            maxlen=0

    def save_item(self,fd):
        sfonte=self.join_references(self.references)
        pfonte=self.join_references(self.references_pron)
        args=[self.occasione,self.voce,pfonte,self.pronuncia,sfonte]
        txt="\\"+self.tipo
        if self.cosa_guardare:
            txt+="["+self.cosa_guardare+"]"
        txt+="{"+"}{".join(args)+"}\n"
        fd.write(txt)

    def print_item_base(self,fd,bullet="",color=""):
        if DRAFT and color:
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
        if DRAFT and bullet:
            fd.write("\\item["+bullet+"] "+txt+virg+pron)
        else:
            fd.write("\\item["+txt+virg+"]"+pron)

    def print_item_pronuncia_base(self,fd,bullet="",color=""):
        if DRAFT and color:
            if bullet: bullet="{\\color{"+color+"}"+bullet+"}"
            txt="{\\color{"+color+"}\\sf "+self.pronuncia.strip()+"}"
        else:
            txt="{\\sf "+self.pronuncia.strip()+"}"
        if DRAFT and bullet:
            fd.write("\\item["+bullet+"] "+txt)
        else:
            fd.write("\\item["+txt+"]")
        fd.write(" "+spzrl(self.voce.strip()))

class VOttVariante(TRiga):
    def __init__(self,data):
        TRiga.__init__(self,data,1,"vottvariante","variante")

    def print_item(self,fd,bullet="",color=""):
        if not DRAFT and color=="colorsologlossario": return
        self.print_item_base(fd,bullet=bullet,color=color)
        if not self.matches: return
        if not DRAFT: return
        fd.write("\\begin{subvocedue}\n")
        for (sim,par) in self.matches:
            par.print_item(fd,bullet="("+str(sim)+")")
        fd.write("\\end{subvocedue}\n")

    def print_item_base(self,fd,bullet="",color=""):
        TRiga.print_item_base(self,fd,bullet=bullet,color=color)
        if self.occasione: fd.write(", "+self.occasione)
        self.print_references(fd)

    def print_item_pronuncia(self,fd,bullet="",color=""):
        self.print_item_pronuncia_base(fd,bullet=bullet,color=color)
        fd.write("\n")

class VoceTurca(TRiga):
    def __init__(self,data,tipo,sezione):
        self.verificare=False
        self.noteverificare=""
        TRiga.__init__(self,data,2,tipo,sezione)
        self.varianti=[]

    def split_args(self):
        ( categorie,self.origine,self.voce,
          pfonte,self.pronuncia,self.significato,sfonte)=self.args
        if self.fac_args:
            self.cosa_guardare=self.fac_args[0]
        else:
            self.cosa_guardare=""
        self.references_pron=self.split_references(pfonte)
        self.references=self.split_references(sfonte)
        if categorie.strip():
            self.categorie=categorie.strip().split(":")
        else:
            self.categorie=[]
        punt_re=re.compile(" +([.,;:])")
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
        categorie=":".join(self.categorie)
        signif=self.significato
        if self.verificare:
            signif+=" \\verificare"
            if self.noteverificare:
                signif+="["+self.noteverificare+"]"
        args=[categorie,self.origine,self.voce,
              pfonte,self.pronuncia,signif,sfonte]
        txt="\\"+tipo
        if self.cosa_guardare:
            txt+="["+self.cosa_guardare+"]"
        txt+="{"+"}{".join(args)+"}\n"
        fd.write(txt)

    def is_radice(self,parola):
        if TRiga.is_radice(self,parola): return(True)
        for v in self.varianti:
            if v.is_radice(parola): return(True)
        return(False)

    def get_suffissi(self):
        suff=[]
        for (match,par) in self.matches:
            if type(match)==GMatchSimil: continue
            if TRiga.is_radice(self,par):
                s=self.dividi_suffisso(par.realword)
                if not s: continue
                p=ParSuffisso(s)
                if p not in suff:
                    suff.append(p)
                else:
                    ind=suff.index(p)
                    p=suff[ind]
                p.parole.append(par)
                continue
        for v in self.varianti:
            vsuff=v.get_suffissi()
            for p in vsuff:
                if p not in suff:
                    suff.append(p)
                else:
                    ind=suff.index(p)
                    suff[ind].parole+=p.parole
        return(suff)

    def get_divisioni(self):
        divisioni=[]
        for (match,par) in self.matches:
            if type(match)==GMatchSimil:
                divisioni.append((par,''))
                continue
            if TRiga.is_radice(self,par):
                s=self.dividi_suffisso(par.realword)
                if not s:
                    divisioni.append((par,''))
                    continue
                divisioni.append((par,s))
        for v in self.varianti:
            divisioni+=v.get_divisioni()
        return(divisioni)

    def len_radice(self,parola):
        if self.is_radice(parola):
            maxlen=len(self)
        else:
            maxlen=0
        for v in self.varianti:
            L=v.len_radice(parola)
            maxlen=max(maxlen,L)
        if self.is_verbo():
            maxlen+=0.5
        return(maxlen)

    def simil(self,parola):
        sim=TRiga.simil(self,parola)
        if sim==1: return(sim)
        maxsim=sim
        for v in self.varianti:
            sim=v.simil(parola)
            maxsim=max(maxsim,sim)
        return(maxsim)

    def print_item_base(self,fd,bullet="",color=""):
        TRiga.print_item_base(self,fd,bullet=bullet,color=color)
        tcat=""
        if self.categorie:
            tcat+="/".join(map(lambda x: x.strip()+".",self.categorie))
        if self.origine.strip():
            tcat+="\\ "+self.origine.lower().strip()+"."
        if tcat:
            fd.write(",\\ "+tcat)
        fd.write(":\\ ")
        if self.significato:
            fd.write(self.significato)
            if DRAFT and self.verificare:
                fd.write(" \\verificare")
                if self.noteverificare:
                    fd.write("["+self.noteverificare+"]")
            fd.write(".")
        fd.write("\n")
        self.print_references(fd)

class VoceOttomana(VoceTurca):
    def __init__(self,data,sub=False):
        VoceTurca.__init__(self,data,"voceottomana","Turco")
        self.sub=sub
        self.subvoci=[]
        self.indice=1

    def __eq__(self,other):
        if type(other)==Parola:
            return(self.parola.__eq__(other))
        flag=self.parola.__eq__(other.parola)
        if not flag: return(flag)
        return(self.indice==other.indice)

    # deve ritornare il numero di parole che matchano
    def get_cardinalita(self):
        if not self.matches: return(0)
        C=0
        for (sim,par) in self.matches:
            C+=par.get_cardinalita()
        return(C)

    def is_radice(self,parola):
        if VoceTurca.is_radice(self,parola): return(True)
        for v in self.subvoci:
            if v.is_radice(parola): return(True)
        return(False)

    def get_suffissi(self):
        suff=VoceTurca.get_suffissi(self)
        for v in self.subvoci:
            vsuff=v.get_suffissi()
            for p in vsuff:
                if p not in suff:
                    suff.append(p)
                else:
                    ind=suff.index(p)
                    suff[ind].parole+=p.parole
        return(suff)

    def get_divisioni(self):
        divisioni=VoceTurca.get_divisioni(self)
        for v in self.subvoci:
            divisioni+=v.get_divisioni()
        return(divisioni)

    def save_item(self,fd,tipo=""):
        VoceTurca.save_item(self,fd,tipo)
        if self.varianti:
            for s in self.varianti:
                s.save_item(fd)
        if self.subvoci:
            for s in self.subvoci:
                s.save_item(fd,tipo="subvoceottomana")

    def print_item(self,fd,bullet="",color=""):
        if not DRAFT and color=="colorsologlossario": return
        self.print_item_base(fd,bullet=bullet,color=color)

        if not (self.subvoci or self.matches or self.varianti):
            return

        if (not DRAFT and not self.varianti): return

        fd.write("\\begin{subvocedue}\n")

        if self.varianti:
            if DRAFT: b="(var)"
            else: b="var.:"
            for s in self.varianti:
                s.print_item(fd,bullet=b)

        if not DRAFT:
            fd.write("\\end{subvocedue}\n")
            return
        if self.subvoci:
            for s in self.subvoci:
                s.print_item(fd,bullet="\\subglossariobullet")
            
        if self.matches: 
            for (sim,par) in self.matches:
                par.print_item(fd,bullet="("+str(sim)+")")
        fd.write("\\end{subvocedue}\n")


    # \spzlessottomano{arabtex}{pronuncia}{significato}
    def print_item_base_cat(self,fd):
        txt=self.voce.strip()
        pron=self.pronuncia.strip()
        sign=self.significato.strip()
        fd.write("\\spzlessottomano{"+txt+"}{"+pron+"}{"+sign+"}\n")
        tcat=""
        if self.categorie:
            tcat+="/".join(map(lambda x: x.strip()+".",self.categorie))
        if self.origine.strip():
            tcat+="\\ "+self.origine.lower().strip()+"."
        if tcat:
            fd.write(",\\ "+tcat)
        fd.write("\n")
        if self.significato:
            fd.write(self.significato)
            if DRAFT and self.verificare:
                fd.write(" \\verificare")
                if self.noteverificare:
                    fd.write("["+self.noteverificare+"]")
            fd.write(".")
        fd.write("\n")
        self.print_references(fd)

    ### ITEMCAT
    def print_item_cat(self,fd):
        self.print_item_base_cat(fd)
        if not (self.subvoci or self.matches or self.varianti):
            return
        fd.write("\\begin{subvocedue}\n")
        if self.varianti:
            for s in self.varianti:
                s.print_item(fd,bullet="(var)")
        if self.subvoci:
            for s in self.subvoci:
                s.print_item(fd,bullet="\\subglossariobullet")
        if self.matches: 
            for (sim,par) in self.matches:
                par.print_item(fd,bullet="("+str(sim)+")")
        fd.write("\\end{subvocedue}\n")

    def print_item_pronuncia(self,fd,bullet="",color=""):
        self.print_item_pronuncia_base(fd,bullet=bullet,color=color)
        fd.write("\n")
        if not (self.subvoci  or self.varianti):
            return
        fd.write("\\begin{subvocedue}\n")
        if self.varianti:
            for s in self.varianti:
                s.print_item_pronuncia(fd,bullet="(var)")
        if self.subvoci:
            for s in self.subvoci:
                s.print_item_pronuncia(fd)
        fd.write("\\end{subvocedue}\n")


def decidi_colore(voce,subvoce=False):
    from Suffissi import Suffissi,Suffisso

    remen=re.compile(".*meninski.*")
    reste=re.compile(".*steingass.*")
    relan=re.compile(".*lane.*")

    # le funzioni di test ritornano  False se va tutto bene (=> nessun
    # colore) e True se ci sono problemi (=> colora)
    def test_nonorigine(voce):
        if subvoce: return(False)
        if type(voce)==VOttVariante: return(False)
        if type(voce)==Suffisso:
            return(not (voce.origine))
        if "np" in voce.categorie: return(False)
        return(not (voce.origine and voce.categorie))

    def test_nonref(voce): return(not bool(voce.references))

    def test_nonrefpron(voce): return(not bool(voce.references_pron))

    def test_lowref(voce):
        if not voce.references: return(True)
        if voce.references.has_key("sec"): return(False)
        if voce.references.has_key("tab"): return(False)
        for r in voce.references["bib"]:
            if remen.match(r[0]): return(False)
            if reste.match(r[0]): return(False)
            if relan.match(r[0]): return(False)
        return(True)

    def test_lowrefpron(voce):
        if not voce.references_pron: return(True)
        if voce.references_pron.has_key("sec"): return(False)
        if voce.references_pron.has_key("tab"): return(False)
        for r in voce.references["bib"]:
            if remen.match(r[0]): return(False)
        return(True)
        
    def test_nosignificato(voce):
        if type(voce)==VOttVariante: return(False)
        return(voce.significato.strip()=="")
        
    ftest={ "nonorigine": test_nonorigine,
            "nonref": test_nonref,
            "nonrefpron": test_nonrefpron,
            "lowref": test_lowref,
            "lowrefpron": test_lowrefpron,
            "nosignificato": test_nosignificato }
    cord=map(str,COLORI_ORDINE)
    cord.reverse()
    if type(voce) in [Parola,ParSuffisso]:
        return( ("colorsolodoc","{\\bf (d)}") )
    if not voce.matches and not subvoce:
        return( ("colorsologlossario","{\\bf (g)}") )
    color=""
    for t in cord:
        if not COLORA[t]: continue
        if ftest[t](voce): color="color"+t
    return( (color,"") )
