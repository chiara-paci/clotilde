# -*- coding: utf-8 -*-

from config import *
import os
import re
from Parola import Parola
import sys

## voce.categoria  deve  diventare  un  array;  nel  parsing,  diventa
## cat1:cat2:cat3 ecc.  perché ci sono  parole che appartengono  a più
## categorie

## voce.next/prev anche per le subvoci

class GMatch(object):
    def __init__(self,tipo,order=0,level=0):
        self.tipo=tipo
        self.order=order
        self.level=level

    def __str__(self):
        return(self.tipo)

    def __gt__(self,other):
        if self.order!=other.order:
            return(self.order>other.order)
        return(self.level>other.level)

    def __lt__(self,other): return(other.__gt__(self))

    def __le__(self,other):
        return( (self.__eq__(other) or self.__lt__(other)) )

    def __ge__(self,other):
        return( (self.__eq__(other) or self.__gt__(other)) )

    def __eq__(self,other):
        return( ((self.order==other.order) and (self.level==other.level)) )

    def __ne__(self,other): return(not(self.__eq__(other)))

    def loc_gt(self,other): return(False)

class GMatchSimil(GMatch):
    def __init__(self,level):
        GMatch.__init__(self,"simil",order=10,level=level)

    def __str__(self):
        return(self.tipo+":"+str(self.level))

class GMatchRadice(GMatch):
    def __init__(self,level):
        GMatch.__init__(self,"radice",level=level)

class GRiga(object):
    def __init__(self,data,voceind,tipo,sezione):
        self.data=data
        self.tipo=tipo
        Q="^."+self.tipo
        self.text=re.sub(Q,"",self.data)
        self.args=[]
        self.fac_args=[]
        self.estrai_args()
        self.parola=Parola(self.args[voceind],sezione)
        self.matches=[]

    def get_primo_carattere(self): return(self.parola.get_primo_carattere())

    def is_verbo(self): return(False)

    def __len__(self): return(len(self.parola))

    def __str__(self):
        T=" ".join(self.args)
        return(T)

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

    def __hash__(self): return(id(self))

    def __eq__(self,other):
        if type(other)==Parola:
            return(self.parola.__eq__(other))
        return(self.parola.__eq__(other.parola))

    def __ne__(self,other):
        if type(other)==Parola:
            return(self.parola.__ne__(other))
        return(self.parola.__ne__(other.parola))

    def __lt__(self,other):
        if type(other)==Parola:
            return(self.parola.__lt__(other))
        return(self.parola.__lt__(other.parola))

    def __gt__(self,other):
        if type(other)==Parola:
            return(self.parola.__gt__(other))
        return(self.parola.__gt__(other.parola))

    def __le__(self,other):
        if type(other)==Parola:
            return(self.parola.__le__(other))
        return(self.parola.__le__(other.parola))

    def __ge__(self,other):
        if type(other)==Parola:
            return(self.parola.__ge__(other))
        return(self.parola.__ge__(other.parola))

    def simil(self,other):
        if type(other)==Parola:
            return(self.parola.simil(other))
        return(self.parola.simil(other.parola))

    def print_item(self,fd,bullet=""): pass

class VoceAraba(GRiga):
    def __init__(self,data):
        GRiga.__init__(self,data,0,"vocearaba","Arabo")
        ( self.voce,self.radice,
          self.significato_base,self.significato,sfonte )=self.args
        self.references={}
        for sref in sfonte.split(";"):
            r=sref.split("/")
            if len(r)<=1: continue
            if not self.references.has_key(r[0]):
                self.references[r[0]]=[]
            self.references[r[0]].append(r[1:])


    def print_item(self,fd,bullet="",color=""):
        if color:
            if bullet: bullet="{\\color{"+color+"}"+bullet+"}"
            txt="{\\color{"+color+"}"+spzrl(self.radice.strip())+"}"
        else:
            txt=spzrl(self.radice.strip())
        if bullet:
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

        fd.write("\\begin{subvocedue}\n")
        if self.references:
            fd.write("\\item[Rif.:] ")
            L=[]
            for k in [ "sec", "bib" ]:
                if self.references.has_key(k):
                    L+=map(map_sec,self.references[k])
            txt=", ".join(L)
            fd.write(txt+"\n")
        fd.write("\\end{subvocedue}\n")


class TRiga(GRiga):
    def __init__(self,data,voceind,tipo,sezione):
        self.references={}
        self.references_pron={}
        GRiga.__init__(self,data,voceind,tipo,sezione)
        self.split_args()
        self.mk_regexp()

    def print_references(self,fd):
        if not self.references and not self.references_pron: return

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

        fmap={"bib": map_bib, "sec": map_sec}

        fd.write("\\begin{subvocedue}\n")
        if self.references_pron:
            fd.write("\\item[Pron. ("+str(self.pron_valutazione())+"):] ")
            L=[]
            for k in [ "sec", "bib" ]:
                if self.references_pron.has_key(k):
                    L+=map(fmap[k],self.references_pron[k])
            txt=", ".join(L)
            fd.write(txt+"\n")
        if self.references:
            fd.write("\\item[Rif.:] ")
            L=[]
            for k in [ "sec", "bib" ]:
                if self.references.has_key(k):
                    L+=map(fmap[k],self.references[k])
            txt=", ".join(L)
            fd.write(txt+"\n")
        fd.write("\\end{subvocedue}\n")

    def is_verbo(self): return(self.parola.word[-1]=="B")

    def split_args(self):
        ( self.occasione,self.voce,pfonte,self.pronuncia,sfonte )=self.args
        if self.fac_args:
            self.cosa_guardare=self.fac_args[0]
        else:
            self.cosa_guardare=""
        self.split_references(pfonte,sfonte)

    def split_references(self,pfonte,sfonte):
        self.references_pron={}
        for pref in pfonte.split(";"):
            r=pref.split("/")
            if len(r)<=1: continue
            if not self.references_pron.has_key(r[0]):
                self.references_pron[r[0]]=[]
            self.references_pron[r[0]].append(r[1:])

        self.references={}
        for sref in sfonte.split(";"):
            r=sref.split("/")
            if len(r)<=1: continue
            if not self.references.has_key(r[0]):
                self.references[r[0]]=[]
            self.references[r[0]].append(r[1:])

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
        self.regexp="^"+base
        self.re=re.compile(r''+self.regexp)

    def is_radice(self,parola):
        R=self.re.match(parola.realword)
        return(R)

    def len_radice(self,parola):
        if self.is_radice(parola):
            maxlen=len(self)
        else:
            maxlen=0

    def print_item_base(self,fd,bullet="",color=""):
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

    def print_item_pronuncia_base(self,fd,bullet="",color=""):
        if color:
            if bullet: bullet="{\\color{"+color+"}"+bullet+"}"
            txt="{\\color{"+color+"}\\sf "+self.pronuncia.strip()+"}"
        else:
            txt="{\\sf "+self.pronuncia.strip()+"}"
        if bullet:
            fd.write("\\item["+bullet+"] "+txt)
        else:
            fd.write("\\item["+txt+"]")
        fd.write(" "+spzrl(self.voce.strip()))

class VOttVariante(TRiga):
    def __init__(self,data):
        TRiga.__init__(self,data,1,"vottvariante","variante")

    def print_item(self,fd,bullet="",color=""):
        self.print_item_base(fd,bullet=bullet,color=color)
        if not self.matches: return
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
        TRiga.__init__(self,data,2,tipo,sezione)
        self.varianti=[]

    def split_args(self):
        ( categorie,self.origine,self.voce,
          pfonte,self.pronuncia,self.significato,sfonte)=self.args
        if self.fac_args:
            self.cosa_guardare=self.fac_args[0]
        else:
            self.cosa_guardare=""
        self.split_references(pfonte,sfonte)
        if categorie.strip():
            self.categorie=categorie.strip().split(":")
        else:
            self.categorie=[]
        punt_re=re.compile(" +([.,;:])")
        self.significato=punt_re.sub(r'\1',self.significato)
        self.significato=self.significato.strip()
        if not self.significato: return
        if self.significato[-1]!=".":
            if self.significato[-1] in [",",":",".",";"]:
                self.significato=self.significato[:-1]
            self.significato+="."

    def is_radice(self,parola):
        if TRiga.is_radice(self,parola): return(True)
        for v in self.varianti:
            if v.is_radice(parola): return(True)
        return(False)

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
        #if self.categoria.strip():
        #    tcat+=self.categoria.strip()+"."
        if self.origine.strip():
            tcat+="\\ "+self.origine.lower().strip()+"."
        if tcat:
            fd.write(",\\ "+tcat)
        fd.write(":\\ ")
        fd.write(self.significato)
        fd.write("\n")
        self.print_references(fd)

class VoceOttomana(VoceTurca):
    def __init__(self,data,sub=False):
        VoceTurca.__init__(self,data,"voceottomana","Turco")
        self.sub=sub
        self.subvoci=[]
        self.alternative=[]

    def print_item(self,fd,bullet="",color=""):
        self.print_item_base(fd,bullet=bullet,color=color)

        if not (self.subvoci or self.alternative or self.matches or self.varianti):
            return

        fd.write("\\begin{subvocedue}\n")
        if self.alternative:
            for s in self.alternative:
                s.print_item(fd,bullet="(omog)")
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
        if not (self.subvoci or self.alternative or self.varianti):
            return
        fd.write("\\begin{subvocedue}\n")
        if self.alternative:
            #n=2
            for s in self.alternative:
                s.print_item_pronuncia(fd,bullet="(omog)")
                #s.print_item_pronuncia(fd,bullet="(omog. "+str(n)+")")
                #n+=1
        if self.varianti:
            for s in self.varianti:
                s.print_item_pronuncia(fd,bullet="(var)")
        if self.subvoci:
            for s in self.subvoci:
                s.print_item_pronuncia(fd)
        fd.write("\\end{subvocedue}\n")

class Glossario(object):
    def __init__(self,finput):
        self.finput=finput
        self.vociottomane=[]
        self.vociarabe=[]
        self.vottgrammaticali={}
        self.matrix=[]
        self.abbreviazioni=set()

    def clear(self):
        self.vottgrammaticali={}
        self.vociottomane=[]
        self.vociarabe=[]


    def match(self,voce,parola):
        if ( (voce.parola.realword=="^EyleB") and
             (parola.realword in ["^Eyledi:k","^Eyley.Hl:ar"]) ):
            print voce.parola.realword,parola.realword
        sim=voce.simil(parola)
        if sim>=0.5:
            if ( (voce.parola.realword=="^EyleB") and
                 (parola.realword in ["^Eyledi:k","^Eyley.Hl:ar"]) ):
                print "sim",sim
            return( GMatchSimil(sim) )
        if not voce.is_radice(parola):
            if ( (voce.parola.realword=="^EyleB") and
                 (parola.realword in ["^Eyledi:k","^Eyley.Hl:ar"]) ):
                print "no"
            return(None)
        L=voce.len_radice(parola)
        if L>0:
            #if voce.is_verbo():
            #    return( GMatchRadice(len(voce)+1000) )
            if ( (voce.parola.realword=="^EyleB") and
                 (parola.realword in ["^Eyledi:k","^Eyley.Hl:ar"]) ):
                print "len",L
            return( GMatchRadice(L) )
        if ( (voce.parola.realword=="^EyleB") and
             (parola.realword in ["^Eyledi:k","^Eyley.Hl:ar"]) ):
            print "no2"
        return(None)

    def add_parole(self,parole,num_righe,num_colonne):
        solo_doc=map(lambda x: x, parole)
        par_matches={}
        liste=[self.vociottomane]
        liste+=self.vottgrammaticali.values()
        
        for lista in liste:
            for voce in lista:
                par=[]
                for parola in parole:
                    m=self.match(voce,parola)
                    if not m: continue
                    par.append( (m,parola) )
                    if not par_matches.has_key(parola):
                        par_matches[parola]=[]
                    par_matches[parola].append((m,voce))
                    if parola in solo_doc:
                        solo_doc.remove(parola)
                if par: voce.matches+=par

        for (parola,vlist) in par_matches.items():
            if len(vlist)<=1: continue
            vlist.sort()
            vlist.reverse()
            for v in vlist[1:]:
                v[1].matches.remove((v[0],parola))

        self.solo_doc=solo_doc
        self.reset_matrix(num_righe,num_colonne)

    def reset_matrix(self,num_righe,num_colonne):
        self.matrix=map(lambda y: map(lambda x: None, range(0,num_colonne)),
                        range(0,num_righe))
        tutti=self.solo_doc+self.vociottomane
        for voce in tutti:
            primo=voce.get_primo_carattere()
            if type(voce)==Parola:
                for (r,cols) in voce.righe.items():
                    for c in cols:
                        self.matrix[r][c]=voce
                continue
            if not voce.matches:
                continue
            for (sim,par) in voce.matches:
                for (r,cols) in par.righe.items():
                    for c in cols:
                        self.matrix[r][c]=(par,voce,sim)

        for (catid,lista) in self.vottgrammaticali.items():
            for voce in lista:
                if not voce.matches: continue
                for (sim,par) in voce.matches:
                    for (r,cols) in par.righe.items():
                        for c in cols:
                            self.matrix[r][c]=(par,voce,sim,catid)

    def next_cell(self,r,c):
        max_ind=len(self.matrix[r])-1
        while not self.matrix[r][max_ind]: max_ind-=1
        if c<max_ind: return((r,c+1))
        if r<len(self.matrix)-1:
            return((r+1,0))
        return((None,None))

    def prev_cell(self,r,c):
        if c>0: return( (r,c-1) )
        if r==0: return((None,None))
        max_ind=len(self.matrix[r-1])-1
        while not self.matrix[r-1][max_ind]: max_ind-=1
        return((r-1,max_ind))

    def range_matrix(self,r,c,qta):
        ret=[self.matrix[r][c]]
        if qta>0:
            for n in range(0,qta):
                (r,c)=self.next_cell(r,c)
                if not r: return(ret)
                ret.append(self.matrix[r][c])
            return(ret)
        for n in range(0,-qta):
            (r,c)=self.prev_cell(r,c)
            if not r: return(ret)
            ret.insert(0,self.matrix[r][c])
        return(ret)

    def print_items_abbreviazioni(self,fd):
        fd.write("\\begin{footnotesize}\n")
        fd.write("""Sono {\it voci} le voci nel glossario che segue. Sono {\it parole}
        quelle che compaiono nel testo. Due varianti sono due modi
        diversi di scrivere o leggere la stessa voce.  Due omografi
        sono due voci che si scrivono nello stesso modo ma hanno
        orgine e significato diversi. Una voce è considerata simile a
        una parola se ha le stesse lettere (senza considerare le
        harakat); viene dato anche un indice di similitudine da~0.0
        (nessuna corrispondenza) a~1.0 (identità).  Una voce è
        considerata radice di una parola se l'inizio della parola
        corrisponde esattamente alla radice (considerando anche le
        harakat e la trascrizione).  La somiglianza è considerata più
        forte dell'essere una radice. Le parole prese dal testo sono
        seguite dall'indice delle righe in cui compaiono e, tra
        parentesi, la posizione della parola nella riga (partendo
        da~0). Di alcune parole viene dato il contesto in cui
        compaiono. Il contesto è determinato dalla voce (non dalla
        parola), cioè ogni voce specifica se è necessario considerare
        il contesto e quante parole prima o dopo devono essere prese
        per formarlo.""")
        fd.write("\n\\end{footnotesize}\n\n")
        fd.write("\\vfill\n\n")
        labels={ "var": "variante",
                 "omog": "omografo",
                 "radice": "la voce è radice di",
                 "simil": "la voce è simile a" }
        def loc_tostr(key,finale="\\\\"):
            if key in self.abbreviazioni:
                label=key.lower()
            else:
                label="{\\color{red}"+key.lower()+"}"
            T=label+".\ &"+ABBREVIAZIONI[key]+finale+"\n"
            return(T)
        for (nome,desc) in COLORI.items():
            fd.write("\\definecolor{color"+nome+"}{rgb}")
            fd.write("{"+",".join(map(str,desc))+"}\n")
        fd.write("\n")
        abbr=ABBREVIAZIONI.keys()
        abbr.sort(cmp=lambda x,y: cmp(x.lower(),y.lower()))
        fd.write("\\begin{center}\n")
        fd.write("\\noindent{\sc Abbreviazioni}\n\n\\vspace{1em}\n\n")
        fd.write("\\noindent{\\footnotesize\\begin{tabular}{*{2}{>{\it}l}}\n")

        # 2 colonne
        #labkeys=[ "omog", "radice", "simil", "var" ]
        #K=len(labkeys)
        #L=len(abbr)
        #N=L+K
        #M=int(round(N/2.0))

        #for n in range(0,M):
        #    fd.write(loc_tostr(abbr[n],finale=" & "))
        #    if n+M<L:
        #        fd.write(loc_tostr(abbr[n+M]))
        #        continue
        #    if n+M<L+K:
        #        lab=labkeys[n+M-L]
        #        fd.write("("+lab+") & "+labels[lab]+"\\\\\n")
        
        for a in abbr:
            fd.write(loc_tostr(a))
        for lab in [ "omog", "radice", "simil", "var" ]:
            fd.write("("+lab+") & "+labels[lab]+"\\\\\n")

        fd.write("\\end{tabular}}\n\n")
        fd.write("\\end{center}\n")
        fd.write("\\newpage\n\n")

    def decidi_colore(self,voce):
        def test_nonorigine(voce): return(not (voce.origine and voce.categorie))
        def test_nonref(voce): return(not bool(voce.references))
        def test_nonrefpron(voce): return(not bool(voce.references_pron))
        def test_nosignificato(voce): return(voce.significato.strip()=="")
        ftest={ "nonorigine": test_nonorigine,
                "nonref": test_nonref,
                "nonrefpron": test_nonrefpron,
                "nosignificato": test_nosignificato }
        cord=map(str,COLORI_ORDINE)
        cord.reverse()
        if type(voce)==Parola:
            return( ("colorsolodoc","{\\bf (d)}") )
        if not voce.matches:
            return( ("colorsologlossario","{\\bf (g)}") )
        color=""
        for t in cord:
            if not COLORA[t]: continue
            if ftest[t](voce): color="color"+t
        return( (color,"") )

    def print_items_grammaticali(self,fd):
        def begin_secglossario(fd,ind):
            fd.write("\\begin{secglossario}{"+GRAMMATICALI[ind]+"}\n")
            
        def end_secglossario(fd):
            fd.write("\\end{secglossario}\n")
        for k in ORDINE_GRAMMATICALI:
            if not self.vottgrammaticali.has_key(k): continue
            lista=self.vottgrammaticali[k]
            begin_secglossario(fd,k)
            lista.sort()
            for voce in lista:
                (color,bullet)=self.decidi_colore(voce)
                if bullet:
                    voce.print_item(fd,bullet=bullet,color=color)
                    continue
                if not color:
                    voce.print_item(fd)
                else:
                    voce.print_item(fd,color=color)
            end_secglossario(fd)

    def print_items_lessico(self,fd):
        def begin_glossario(fd,ind):
            if ind>=0:
                fd.write("\\begin{glossario}{\\RL{"+LETTERE[ind][0]+"}}\n")
            else:
                fd.write("\\begin{glossario}{Mancanti}\n")
            
        def end_glossario(fd):
            fd.write("\\end{glossario}\n")

        def loc_cella_word(C):
            if type(C)==tuple: return(C[0].word)
            return(C.word)

        tutti=self.solo_doc+self.vociottomane
        tutti.sort()

        fd.write("\\section{Lessico}\n")
        lett_ind=0
        begin_glossario(fd,lett_ind)
        for voce in tutti:
            primo=voce.get_primo_carattere()
            if primo in HARAKAT_TUTTE:
                primo="A"
            elif primo in MULTIPLE.keys():
                primo=MULTIPLE[primo][0]
            elif primo in MULTIPLE_INIZIO.keys():
                primo=MULTIPLE_INIZIO[primo][0]
            if lett_ind!=-1:
                if primo=="-":
                    lett_ind=-1
                    end_glossario(fd)
                    begin_glossario(fd,lett_ind)
                elif ( primo not in LETTERE[lett_ind]):
                    while voce.get_primo_carattere() not in LETTERE[lett_ind]:
                        lett_ind+=1
                    end_glossario(fd)
                    begin_glossario(fd,lett_ind)

            (color,bullet)=self.decidi_colore(voce)
            if bullet:
                voce.print_item(fd,bullet=bullet,color=color)
                continue
            if not color:
                voce.print_item(fd)
            else:
                voce.print_item(fd,color=color)
            if not voce.cosa_guardare: continue
            fd.write("\n\nContesti:\n")
            fd.write("\\begin{subvocedue}\n")
            t=voce.cosa_guardare.split(":")
            if len(t)==1: qta=1
            else: qta=int(t[1])
            if t[0]!="next": qta=-qta
            for (sim,par) in voce.matches:
                for (r,cols) in par.righe.items():
                    for c in cols:
                        label="(riga "+str(r+1)+")"
                        T=" ".join(map(loc_cella_word,self.range_matrix(r,c,qta)))
                        fd.write("\\item["+label+"] ")
                        fd.write(spzrl(T)+"\n")
            fd.write("\\end{subvocedue}\n")
        end_glossario(fd)

    def print_items_arabo(self,fd):
        self.vociarabe.sort()
        fd.write("\\begin{secglossario}{Lessico della parte in arabo}\n")
        for voce in self.vociarabe: voce.print_item(fd)
        fd.write("\\end{secglossario}\n")

    def print_items_pronunce(self,fd):
        def begin_pronunce(fd):
            fd.write("\\begin{secglossario}{Ordine secondo la pronuncia}\n")
            
        def end_pronunce(fd):
            fd.write("\\end{secglossario}\n")

        #tutti=reduce(lambda x,y: x+list(y),
        #             [self.vociottomane]+list(self.vottgrammaticali.items()))
        tutti=self.vociottomane
        tutti.sort(cmp=lambda x,y: cmp(x.pronuncia.lower(),y.pronuncia.lower()))

        begin_pronunce(fd)
        for voce in tutti:
            voce.print_item_pronuncia(fd)
        end_pronunce(fd)
            

    def print_items(self,fd):
        fd.write("\\twocolumn[\\chapter{Glossario}]\n\n")
        self.print_items_abbreviazioni(fd)
        self.print_items_lessico(fd)
        self.print_items_grammaticali(fd)
        self.print_items_arabo(fd)
        self.print_items_pronunce(fd)
        fd.write("\\onecolumn\n\n")

    def print_matrix(self,fd):
        def out_tab(cella):
            if not cella: return("--")
            if type(cella)==tuple:
                par=cella[0]
            else:
                par=cella
            if par.word[0]=="{":
                word_label="\\RL"+par.word
            else:
                word_label="\\RL{"+par.word+"}"
            if type(cella)==tuple:
                if len(cella)==4:
                    return("{\\color{green}"+word_label+"}")
                return(word_label)
            return("{\\color{red}"+word_label+"}")

        fd.write("\\clearpage\n\n")
        fd.write("\\thispagestyle{empty}\n\n")
        #fd.write("\\section{Matrice}\n\n")
        W=500
        H=600
        x0=72
        y0=100
        fd.write("\\begin{picture}("+str(W)+","+str(H)+")")
        fd.write("("+str(x0)+","+str(y0)+")\n")
        #fd.write("\\rettangolo{"+str(W)+"}{"+str(H)+"}\n")
        fd.write("\\put(0,0){\\rotatebox{90}{\\resizebox{0.9\\paperheight}{!}{\n")
        fd.write("\\begin{tabular}{*{"+str(len(self.matrix[0]))+"}{c}r}\n")
        n=1
        for r in self.matrix:
            nr=map(out_tab,r)
            nr.reverse()
            fd.write("&".join(nr)+"&"+str(n)+"\\\\[1.2cm]\n")
            fd.write("\\hline\n")
            n+=1
        fd.write("\\end{tabular}\n")
        fd.write("}}}\n")
        fd.write("\\end{picture}\n")

    def print_stdout(self):
        tutti=self.solo_doc+self.vociottomane
        tutti.sort()

        for voce in tutti:
            if type(voce)==Parola:
                print "+ (D) "+str(voce)
                continue
            if not voce.matches:
                print "+ (G) "+str(voce)
                continue
            print "+ (M) "+str(voce)
            for (sim,p) in voce.matches:
                print "    ("+str(sim)+") "+str(p)

    def print_mini(self):
        for i in self.vociottomane:
            print i.parola

    def print_csv(self):
        print "Ottomane"
        print "========"
        for i in self.vociottomane:
            print i
        print "\n"
        print "Arabe"
        print "====="
        for i in self.vociarabe:
            print i
        print "\n"

    def add_voce(self,tipo,text,lastvott=None,lastnp=None):
        if not tipo: return(lastvott)
        if not text: return(lastvott)
        if tipo=="vocearaba":
            self.vociarabe.append(VoceAraba(text))
            return(None)
        if tipo=="voceottomana":
            vott=VoceOttomana(text)
            if vott in self.vociottomane:
                ind=self.vociottomane.index(vott)
                self.vociottomane[ind].alternative.append(vott)
                return(vott)
            #if vott.categoria: self.abbreviazioni.add(vott.categoria)
            if vott.categorie:
                for c in vott.categorie:
                    self.abbreviazioni.add(c)
            if vott.origine: self.abbreviazioni.add(vott.origine)
            if vott.categorie:
                grammflag=False
                for c in vott.categorie:
                    if c in GRAMMATICALI.keys():
                        grammflag=True
                        if not self.vottgrammaticali.has_key(c):
                            self.vottgrammaticali[c]=[]
                        self.vottgrammaticali[c].append(vott)
                if grammflag: return(vott)
            #if vott.categoria in GRAMMATICALI.keys():
            #    if not self.vottgrammaticali.has_key(vott.categoria):
            #        self.vottgrammaticali[vott.categoria]=[]
            #    self.vottgrammaticali[vott.categoria].append(vott)
            #    return(vott)
            self.vociottomane.append(vott)
            return(vott)
        if tipo=="subvoceottomana":
            svott=VoceOttomana(text,sub=True)
            if lastvott:
                lastvott.subvoci.append(svott)
            #if svott.categoria: self.abbreviazioni.add(svott.categoria)
            if svott.categorie:
                for c in svott.categorie:
                    self.abbreviazioni.add(c)
            if svott.origine: self.abbreviazioni.add(svott.origine)
        if tipo=="vottvariante":
            if lastvott:
                lastvott.varianti.append(VOttVariante(text))
        return(lastvott)
    
    def load(self):
        if not self.finput: return
        if self.finput=="-":
            fd=sys.stdin
        else:
            if not os.path.exists(self.finput): return
            fd=open(self.finput,'r')
        self.clear()
        inizio_riga={"vocearaba":re.compile("^.vocearaba{.*"),
                     "voceottomana":re.compile("^.voceottomana(\[.*\])*{.*"),
                     "subvoceottomana":re.compile("^.subvoceottomana(\[.*\])*{.*"),
                     "vottvariante":re.compile("^.vottvariante{.*")}
        tipo_re=re.compile("^.([^{[ ]*)[{[].*")
        cont_re=re.compile("^ .*")
        comm_re=re.compile("%.*")

        currenttxt=""
        tipo=""
        lastvott=None
        
        for row in fd.readlines(): 
            r=row.replace("\n","").strip()
            if ( (not r) or (comm_re.match(r)) ):
                lastvott=self.add_voce(tipo,currenttxt,lastvott)
                tipo=""
                currenttxt=""
                continue
            if cont_re.match(row):
                if currenttxt:
                    currenttxt+=" "+r
                continue
            t=tipo_re.findall(r)
            if ( (not t) or (t[0] not in inizio_riga.keys()) ):
                lastvott=self.add_voce(tipo,currenttxt,lastvott)
                tipo=""
                currenttxt=""
                continue

            lastvott=self.add_voce(tipo,currenttxt,lastvott)

            tipo=t[0]
            currenttxt=r

        lastvott=self.add_voce(tipo,currenttxt,lastvott)
        fd.close()
        self.vociottomane.sort()
