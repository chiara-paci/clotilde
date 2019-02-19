# -*- coding: utf-8 -*-

from config import *
import os
import re
from Parola import Parola,ParSuffisso
import sys
import time

from Statistiche      import Statistiche
from GCategorizzatore import GCatCategoria,GCatOrigine,GCatOrigineCategoria,GCatMarbuta,GCatNoCat, GCatNoOrig, GCatOrigineNot
from GMatch           import GMatchSimil,GMatchRadice
from Voci             import VoceAraba,VoceOttomana,VOttVariante,decidi_colore
from Suffissi         import Suffissi,Suffisso
from Pronuncie        import Pronuncie
from FormeArabe       import FormeArabe

## voce.next/prev anche per le subvoci

class Glossario(object):
    def __init__(self,finput,suffissi="",formearabe="",pronuncie=""):
        self.finput={ "glossario":  finput,
                      "suffissi":   suffissi,
                      "pronuncie": pronuncie,
                      "formearabe": formearabe }
        self.vociottomane=[]
        self.vociarabe=[]
        self.vottgrammaticali={}
        self.matrix=[]
        self.statistiche=None
        self.abbreviazioni=set()
        self.abbr_valide=set()
        self.categorizzatori=[]
        self.categorizzatori.append(GCatMarbuta(self))
        self.categorizzatori.append(GCatNoCat(self))
        self.categorizzatori.append(GCatNoOrig(self))
        for k in TUTTE_CATEGORIE.keys():
            self.categorizzatori.append(GCatCategoria(self,k))
        for k in ORIGINI.keys():
            self.categorizzatori.append(GCatOrigine(self,k))
        self.categorizzatori.append(GCatOrigineNot(self,"A"))
        for k in ORIGINI.keys():
            for m in ["v", "n", "va", "agg", "avv", "aggc", "aggs"]:
                self.categorizzatori.append(GCatOrigineCategoria(self,k,m))
        if suffissi:
            self.suffissi=Suffissi(self.finput["suffissi"])
            self.suffissi.load()
        if pronuncie:
            self.pronuncie=Pronuncie(self.finput["pronuncie"])
            self.pronuncie.load()
        #self.suffissi_solo_doc=[]
        #self.formearabe=FormeArabe(self.finput["formearabe"])
        #self.formearabe.load()
        #self.formearabe_solo_doc=[]

    def set_suffissi(self,suffissi):
        self.finput["suffissi"]=suffissi
        self.suffissi=Suffissi(self.finput["suffissi"])
        self.suffissi.load()

    def set_pronuncie(self,pronuncie):
        self.finput["pronuncie"]=pronuncie
        self.pronuncie=Pronuncie(self.finput["pronuncie"])
        self.pronuncie.load()

    def clear(self):
        self.vottgrammaticali={}
        self.vociottomane=[]
        self.vociarabe=[]

    def match(self,voce,parola):
        sim=voce.simil(parola)
        if sim>=0.5:
            return( GMatchSimil(sim) )
        if not voce.is_radice(parola):
            return(None)
        L=voce.len_radice(parola)
        if L>0:
            return( GMatchRadice(L) )
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
            primo=vlist[0]
            for v in vlist[1:]:
                if not ( (primo[1].parola==v[1].parola)
                         and ( (primo[1].indice>1)
                               or (v[1].indice>1) ) ):
                    v[1].matches.remove((v[0],parola))

        self.solo_doc=solo_doc
        self.reset_matrix(num_righe,num_colonne)
        self.statistiche=Statistiche(self)
        #self.suffissi.add_glossario(self)
        #self.formearabe.add_glossario(self)

#     def match_suff(self,suff,parsuffisso):
#         sim=suff.simil(parsuffisso)
#         if sim>=0.5:
#             return( GMatchSimil(sim) )
#         return(None)

    def print_suffissi_calcolati(self,fd):
        def out_matrix(r,c):
            cella=self.matrix[r][c]
            if not cella: return("--")
            if type(cella)==tuple:
                par=cella[0]
            else:
                par=cella
            S="\\item["+spzrl(par.word)+"] "+str(r+1)+"("+str(c)+")\n"
            return(S)

        fd.write("\\begin{secglossario}{Suffissi}\n")

        suffissi=[]
        for v in self.get_all():
            vsuff=v.get_suffissi()
            for p in vsuff:
                if p not in suffissi:
                    suffissi.append(p)
                else:
                    ind=suffissi.index(p)
                    suffissi[ind].add_le_parole_di(p)
        suffissi.sort()
        for suff in suffissi:
            suff.print_item(fd)
            R=map(int,suff.righe.keys())
            R.sort()
            fd.write("\\begin{subvocedue}\n")
            for r in R:
                for c in suff.righe[r]:
                    fd.write(out_matrix(r,c))
                    pass
            fd.write("\\end{subvocedue}\n")
        fd.write("\\end{secglossario}\n")

#         solo_doc=map(lambda x:x,suffissi)

#         par_matches={}
#         for suff in self.suffissi:
#             par=[]
#             for parsuffisso in suffissi:
#                 m=self.match_suff(suff,parsuffisso)
#                 if not m: continue
#                 par.append( (m,parsuffisso) )
#                 if not par_matches.has_key(parsuffisso):
#                     par_matches[parsuffisso]=[]
#                 par_matches[parsuffisso].append( (m,suff) )
#                 if parsuffisso in solo_doc:
#                     solo_doc.remove(parsuffisso)
#             if par:
#                 suff.matches+=par
                
#         for (parsuffisso,vlist) in par_matches.items():
#             if len(vlist)<=1: continue
#             vlist.sort()
#             vlist.reverse()
#             primo=vlist[0]
#             for v in vlist[1:]:
#                 if not ( primo[1]==v[1] ):
#                     v[1].matches.remove((v[0],parsuffisso))

#         self.suffissi_solo_doc=solo_doc
        
#     def estrai_formearabe(self):
#         #self.formearabe_solo_doc=[]
#         #for v in self.get_all():
#         #    if v.origine.lower() not in ORIGINI_ARABE:
#         #        continue
#         #    self.formearabe_solo_doc+=v.get_formearabe()
#         pass

    def reset_matrix(self,num_righe,num_colonne):
        self.matrix=map(lambda y: map(lambda x: None, range(0,num_colonne)),
                        range(0,num_righe))
        tutti=self.solo_doc+self.vociottomane
        for voce in tutti:
            primo=voce.get_primo_carattere()
            if type(voce) in [Parola,ParSuffisso]:
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

    def get_all(self):
        tutti=map(lambda x: x,self.vociottomane)
        for (catid,lista) in self.vottgrammaticali.items():
            tutti+=lista
        tutti.sort()
        return(tutti)

    def get_all_anche_doc(self):
        tutti=self.solo_doc+self.vociottomane
        for (catid,lista) in self.vottgrammaticali.items():
            tutti+=lista
        tutti.sort()
        return(tutti)

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

    def range_matrix(self,r0,c0,prima,dopo):
        ret=[self.matrix[r0][c0]]
        (rmax,cmax)=(r0,c0)
        (rmin,cmin)=(r0,c0)
        if dopo>0:
            (r,c)=(r0,c0)
            for n in range(0,dopo):
                (r,c)=self.next_cell(r,c)
                if r==None: break
                if self.matrix[r][c]!=None:
                    ret.append(self.matrix[r][c])
            (rmax,cmax)=(r,c)
            #return(ret)
        if prima>0:
            (r,c)=(r0,c0)
            for n in range(0,prima):
                (r,c)=self.prev_cell(r,c)
                if r==None: break
                if self.matrix[r][c]!=None:
                    ret.insert(0,self.matrix[r][c])
            (rmin,cmin)=(r,c)
        return([ret,(rmin,cmin),(rmax,cmax)])


    def print_items_abbreviazioni(self,fd):
        if DRAFT:
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
        #fd.write("\\vfill\n\n")
        #fd.write("\\columnbreak\n\n")
        labels={ "var": "variante",
                 "omog": "omografo",
                 "radice": "la voce è radice di",
                 "simil": "la voce è simile a" }
        def loc_tostr(key,finale="\\\\"):
            if DRAFT:
                if key in self.abbreviazioni:
                    label=key.lower()
                else:
                    # così in due colonne non va
                    label="{\\color{red}"+key.lower()+"}"
            else:
                if key in self.abbr_valide:
                    label=key.lower()
                else:
                    return("")
            T=label+".\ &"+ABBREVIAZIONI[key]+finale+"\n"
            return(T)
        for (nome,desc) in COLORI.items():
            fd.write("\\definecolor{color"+nome+"}{rgb}")
            fd.write("{"+",".join(map(str,desc))+"}\n")
        fd.write("\n")
        abbr=ABBREVIAZIONI.keys()
        abbr.sort(cmp=lambda x,y: cmp(x.lower(),y.lower()))
        fd.write("\\begin{center}\n")
        fd.write("\\noindent{\\footnotesize\\begin{tabular}{*{2}{>{\it}l}}\n")
        fd.write("\\multicolumn{2}{c}{\sc Abbreviazioni}\\\\[1cm]\n")

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
                (color,bullet)=decidi_colore(voce)
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

            (color,bullet)=decidi_colore(voce)
            if bullet:
                voce.print_item(fd,bullet=bullet,color=color)
                continue
            if not color:
                voce.print_item(fd)
            else:
                voce.print_item(fd,color=color)
            if not voce.cosa_guardare: continue
            if not DRAFT: continue
            fd.write("\n\nContesti:\n")
            fd.write("\\begin{subvocedue}\n")

            for (rmin,cmin,rmax,cmax,T) in self.get_contesti(voce):
                if rmin==rmax:
                    label="(riga "+str(rmin+1)+")"
                else:
                    label="(righe "+str(rmin+1)+"-"+str(rmax+1)+")"
                #print label,voce.word
                fd.write("\\item["+label+"] ")
                fd.write(spzrl(T)+"\n")

            fd.write("\\end{subvocedue}\n")
        end_glossario(fd)

    def get_contesti(self,voce):
        def loc_cella_word(C):
            if type(C)==tuple: return(C[0].word)
            return(C.word)

        (prima,dopo)=self.range_contesto(voce)
        ret=[]
        for (sim,par) in voce.matches:
            for (r,cols) in par.righe.items():
                for c in cols:
                    [L,(rmin,cmin),
                     (rmax,cmax)]=self.range_matrix(r,c,prima,dopo)
                    T=" ".join(map(loc_cella_word,L))
                    ret.append((rmin,cmin,rmax,cmax,T))
        return(ret)

    def range_contesto(self,voce):
        if not voce.cosa_guardare: return((0,0))
        t=voce.cosa_guardare.split(";")
        a=t[0].split(":")
        if len(t)>1:
            b=t[1].split(":")
        else:
            b=[]
        if ((not a) and (not b)) or ( (not a[0]) and (not b[0]) ):
            return( (0,0) )

        prima=0
        dopo=0
        if a[0]=="next":
            if len(a)==1:
                dopo=1
            else:
                dopo=int(a[1])
        else:
            if len(a)==1:
                prima=1
            else:
                prima=int(a[1])
            
        if not b or not b[0]: return((prima,dopo))
        if b[0]=="next":
            if len(b)==1:
                dopo=1
            else:
                dopo=int(b[1])
        else:
            if len(b)==1:
                prima=1
            else:
                prima=int(b[1])
                
        return((prima,dopo))

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
        if DRAFT:
            self.print_items_arabo(fd)
            self.print_items_pronunce(fd)
        fd.write("\\onecolumn\n\n")
        fd.write("% FINE: "+time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())+"\n")
        print "FINE GLOSSARIO"

    def save(self,fd):
        tutti=self.vociottomane+self.vociarabe
        tutti+=reduce(lambda x,y: x+y,self.vottgrammaticali.values())
        fd.write("% glossario\n")
        fd.write("\n")
        for voce in tutti:
            voce.save_item(fd)

    def print_statistiche(self,fd,full=True):
        caption="""Statistiche. In ogni cella, la prima riga rappresenta il numero di parole distinte, la seconda tiene conto anche delle ripetizioni.
        """
        if full:
            (Q,col_keys,num_cols,
             num_rows,num_gram,ns_esiste)=self.statistiche.get_sparsa()
        else:
            (Q,col_keys,num_cols,
             num_rows,num_gram,ns_esiste)=self.statistiche.get_nonsparsa()
        
        c_keys=map(lambda x: (x[1],x[0]),col_keys.items())
        c_keys.sort()
        
        c_keys=["altro"]+map(lambda x: ORIGINI[x[1].upper()].lower(),
                             c_keys[2:])

        if ns_esiste:
            NR=num_rows-4
        else:
            NR=num_rows-3

        def r_param(r):
            def perc(n,T):
                if n==0:
                    return("\\multicolumn{3}{c|}{}")
                p=100.0*n/T
                i=str(int(p))
                d="%02d" % int(100*(p-int(p)))
                s=str(n)+"&"+str(i)+"&"+str(d)
                return(s)
                
            lab=Q[r][0]
            tota=reduce(lambda z,y:z+y,map(lambda x: x[0],Q[r][1:]))
            totb=reduce(lambda z,y:z+y,map(lambda x: x[1],Q[r][1:]))
            A=" & ".join(map(lambda x: perc(x[0],tota),Q[r][1:]))
            B=" & ".join(map(lambda x: perc(x[1],totb),Q[r][1:]))
            return(lab,A,B,tota,totb)

        def r_empty():
            lab=""
            A=" & ".join(map(lambda x: "\\multicolumn{3}{c|}{}",range(0,num_cols-1)))
            B=" & ".join(map(lambda x: "\\multicolumn{3}{c|}{}",range(0,num_cols-1)))
            tota=""
            totb=""
            return(lab,A,B,tota,totb)

        def r_print(g_lab,g_A,g_B,g_tota,g_totb):
            fd.write(g_lab.lower()+" & "+str(g_tota)+" & "+g_A+"\\\\\n")
            fd.write(" & "+str(g_totb)+" & "+g_B+"\\\\\n")
            fd.write("\\hline\n")

        ncol=3*(num_cols-1)

        def r_titoletto(titolo):
            fd.write("\\hline\n")
            fd.write("\\multicolumn{"+str(ncol+2)+"}{|c|}{\\it "+titolo+"}")
            fd.write("\\\\\n")
            fd.write("\\hline\n")

        fd.write("\\begin{table}\n")
        fd.write("\\resizebox{\\textwidth}{!}{\\mbox{")
        fd.write("\\begin{tabular}")
        fd.write("{|>{\\it}r|r|*{"+str(num_cols-1)+"}{rr@{.}l@{\% }|}}\n")
        fd.write("\\hline\n")
        t=" & ".join(map(lambda x: "\\multicolumn{3}{c|}{\\it "+x+" }",c_keys))
        fd.write("\\multicolumn{1}{|c}{} & \multicolumn{1}{c|}{\\it totale} &"+t+"\\\\\n")
        fd.write("\\hline\n")
        r_titoletto("grammaticali")
        for r in range(0,num_gram):
            (g_lab,g_A,g_B,g_tota,g_totb)=r_param(r)
            r_print(g_lab,g_A,g_B,g_tota,g_totb)

        fd.write("\\hline\n")
        (g_lab,g_A,g_B,g_tota,g_totb)=r_param(-3)
        r_print(g_lab,g_A,g_B,g_tota,g_totb)

        r_titoletto("lessico")

        for r in range(num_gram,NR):
            (g_lab,g_A,g_B,g_tota,g_totb)=r_param(r)
            r_print(g_lab,g_A,g_B,g_tota,g_totb)

        fd.write("\\hline\n")
        (g_lab,g_A,g_B,g_tota,g_totb)=r_param(-2)
        r_print(g_lab,g_A,g_B,g_tota,g_totb)

        if ns_esiste or bool(self.statistiche.num_nomi_propri[0]):
            fd.write("\\hline\n")

        if ns_esiste:
            (g_lab,g_A,g_B,g_tota,g_totb)=r_param(-4)
            r_print(g_lab,g_A,g_B,g_tota,g_totb)

        [np_tota,np_totb]=self.statistiche.num_nomi_propri
        if np_tota:
            (g_lab,g_A,g_B,g_tota,g_totb)=r_empty()
            g_lab="nomi propri"
            [g_tota,g_totb]=[np_tota,np_totb]
            r_print(g_lab,g_A,g_B,g_tota,g_totb)

        fd.write("\\hline\n")
        (g_lab,g_A,g_B,g_tota,g_totb)=r_param(-1)
        g_tota+=np_tota
        g_totb+=np_totb
        r_print(g_lab,g_A,g_B,g_tota,g_totb)

        fd.write("\\end{tabular}}}\n")
        fd.write("\\caption{"+caption+"}\n")
        fd.write("\\label{tab:statistiche}\n")
        fd.write("\\end{table}\n")

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
            if type(voce) in [Parola,ParSuffisso]:
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
                n=2
                while (vott in self.vociottomane):
                    vott.indice=n
                    n+=1
            abbr_comb=[]
            if vott.categorie:
                for c in vott.categorie:
                    self.abbreviazioni.add(c)
                    self.abbr_valide.add(c)
                    abbr_comb.append(c)
            if vott.origine:
                self.abbreviazioni.add(vott.origine)
                self.abbr_valide.add(vott.origine)
                abbr_comb=map(lambda x: [vott.origine,x],abbr_comb)
            if abbr_comb:
                map(lambda x: self.abbr_valide.add(":".join(x)),
                    abbr_comb)
            if vott.categorie:
                grammflag=False
                for c in vott.categorie:
                    if c in GRAMMATICALI.keys():
                        grammflag=True
                        if not self.vottgrammaticali.has_key(c):
                            self.vottgrammaticali[c]=[]
                        self.vottgrammaticali[c].append(vott)
                if grammflag: return(vott)
            self.vociottomane.append(vott)
            return(vott)
        if tipo=="subvoceottomana":
            svott=VoceOttomana(text,sub=True)
            if lastvott:
                lastvott.subvoci.append(svott)
            if svott.categorie:
                for c in svott.categorie:
                    self.abbreviazioni.add(c)
            if svott.origine: self.abbreviazioni.add(svott.origine)
        if tipo=="vottvariante":
            if lastvott:
                lastvott.varianti.append(VOttVariante(text))
        return(lastvott)
    
    def load(self):
        if not self.finput["glossario"]: return
        if self.finput["glossario"]=="-":
            fd=sys.stdin
        else:
            if not os.path.exists(self.finput["glossario"]): return
            fd=open(self.finput["glossario"],'r')
        self.clear()

        righekeys=[ "vocearaba","voceottomana","subvoceottomana","vottvariante" ]
        
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
            if ( (not t) or (t[0] not in righekeys) ):
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

    def print_cfr(self,fd,doc):
        def out_tab_arab(cella):
            if not cella: return("")
            if type(cella)==tuple:
                v=cella[1]
            else:
                v=cella
            return(v.voce)
        def out_tab_latin(cella):
            if not cella: return("")
            if type(cella)!=tuple: return("\\manca{}")
            return(cella[1].pronuncia)

        if not doc.righe: return
        fd.write("\\section{Trascrizione\\trascrtitoloadd}\n")
        fd.write("\\novocalize\n")
        fd.write("\\setnodocimages\n")
        fd.write("\\setcounter{righetesto}{0}\n")
        fd.write("\\begin{testo}{righedoc}\n")

        n=0
        for R in doc.righe:
            fd.write("%"+str(R.numero)+"\n")
            fd.write(str(R)+"\n")
            if R.tipo=="arabo":
                n+=1
                continue
            fd.write("\n")
            A=" / ".join(map(out_tab_arab,self.matrix[n]))
            L=" / ".join(map(out_tab_latin,self.matrix[n]))
            A=A.strip()
            L=L.strip()
            fd.write("\\temptestoturco{"+A+"}{"+L+"}\n")
            n+=1
            
        fd.write("\\end{testo}\n")

