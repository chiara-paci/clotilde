# -*- coding: utf-8 -*-

from config import *
from Parola import Parola
from Riga   import Riga
import os
import re
import sys

class Documento(object):
    def __init__(self,finput,foutput):
        self.finput=finput
        self.foutput=foutput
        self.righe=[]
        self.words={}
        self.max_len=0

    def clear(self):
        self.righe=[]
        self.max_len=0

    def load(self):
        if not self.finput: return
        if self.finput=="-":
            fd=sys.stdin
        else:
            if not os.path.exists(self.finput): return
            fd=open(self.finput,'r')
        self.clear()
        inizio_riga={"arabo":re.compile("^.itemtestoarabo{.*"),
                     "turco":re.compile("^.itemtestoturco{.*"),
                     "araboturco":re.compile("^.itemtestoaraboturco{.*")}
        aperte=re.compile("{")
        chiuse=re.compile("}")
        txt=""
        status="fuori"
        num_aperte=0
        num_chiuse=0
        num_args={ "arabo":3, "turco":4, "araboturco":5 }
        numero=1
        for r in fd.readlines(): 
            r=r.replace("\n","").strip()
            if not r: continue
            if status=="fuori":
                trovato=False
                for k in ["arabo","turco","araboturco"]:
                    if not inizio_riga[k].match(r): continue
                    trovato=True
                    status=k
                    txt=r
                    num_aperte=len(aperte.findall(txt))
                    num_chiuse=len(chiuse.findall(txt))
                    if num_aperte>num_chiuse: break
                    if num_aperte==num_args[k]:
                        self.righe.append(Riga(numero,k,num_args[k],txt))
                        status="fuori"
                        numero+=1
                    break
                continue
            txt+=" "+r
            num_aperte=len(aperte.findall(txt))
            num_chiuse=len(chiuse.findall(txt))
            if num_aperte>num_chiuse: continue
            if num_aperte>=num_args[k]:
                self.righe.append(Riga(numero,status,num_args[status],txt))
                status="fuori"
                numero+=1
            
        fd.close()

    def parole(self):
        if not self.righe: return
        words={}
        self.max_len=0

        no=re.compile("^.LR{.tref{.*")

        for r_ind in range(0,len(self.righe)):
            tokens=self.righe[r_ind].parole()
            M=len(tokens)
            self.max_len=max(self.max_len,M)
            for w_ind in range(0,M):
                (sez,word)=tokens[w_ind]
                if no.match(word): continue
                if word in TURCHE_IN_ARABO:
                    sez="Turco"
                if not words.has_key(sez):
                    words[sez]={}
                if not words[sez].has_key(word):
                    words[sez][word]=Parola(word,sez)
                words[sez][word].add_pos(r_ind,w_ind)

        self.words={}
        for k in words.keys():
            self.words[k]=words[k].values()
            self.words[k].sort()

    def cerca_simili(self):
        for n in range(0,len(self.words["Turco"])-1):
            stampato=False
            for m in range(n+1,len(self.words["Turco"])):
                wa=self.words["Turco"][n]
                wb=self.words["Turco"][m]
                simind=wa.simil(wb)
                if simind>0.5:
                    if not stampato:
                        wa.print_simil(primo=True)
                        stampato=True
                    wb.print_simil(ind=simind)

    def print_parole(self):
        if not self.foutput: return
        if self.foutput=="-":
            fd=sys.stdout
        else:
            fd=open(self.foutput,'w')
        fd.write("\\section{Parole}\n\n")
        fd.write("\\novocalize\n\n")
        for k in self.words.keys():
            fd.write("\\subsection{"+k+"}\n\n")
            fd.write("\\begin{itemize*}\n")
            for p in self.words[k]:
                p.print_parole(fd)
            fd.write("\\end{itemize*}\n\n")
        if self.foutput!="-":
            fd.close()

    def print_csv(self):
        if not self.foutput: return
        if self.foutput=="-":
            fd=sys.stdout
        else:
            fd=open(self.foutput,'w')
        for k in self.words.keys():
            for p in self.words[k]:
                p.print_csv(fd)
        if self.foutput!="-":
            fd.close()

    def reprint(self):
        if not self.righe: return
        if not self.foutput: return
        if self.foutput=="-":
            fd=sys.stdout
        else:
            fd=open(self.foutput,'w')
        fd.write("\\section{Trascrizione\\trascrtitoloadd}\n")
        fd.write("\\novocalize\n")
        fd.write("\\setnodocimages\n")
        fd.write("\\setcounter{righetesto}{0}\n")
        fd.write("\\begin{testo}{righedoc}\n")
        for r in self.righe:
            fd.write("%"+str(r.numero)+"\n")
            fd.write(str(r)+"\n")
        fd.write("\\end{testo}\n")
        if self.foutput!="-":
            fd.close()
