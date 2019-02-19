# -*- coding: utf-8 -*-

from config import *
import os
import re

from Radice import Radice

class Radici(dict):
    def __init__(self,radici_name,suffissi_name,sep="@"):
	self.radici_name=radici_name
        self.suffissi_name=suffissi_name
	self.sep=sep
        self.radici={}
        self.suffissi={}
        self.word_suffissi={}
        self.word_radici={}
	dict.__init__(self)

    def clear(self):
	for k in self.keys(): 
	    self.__delitem__(k)
        self.radici={}
        self.suffissi={}
        self.word_suffissi={}
        self.word_radici={}

    def save(self,parole):
	if not self.radici_name: return
	if not self.suffissi_name: return
	rtxt=""
        stxt=""
        for p in parole:
            key=p.word
            if self.word_radici.has_key(key):
                val=self.word_radici[key]
                if val:
                    rtxt+=str(key)+self.sep+str(val)+"\n"
                else:
                    rtxt+=str(key)+self.sep+"\n"
            else:
                rtxt+=str(key)+"\n"
            if self.word_suffissi.has_key(key):
                stxt+=str(key)+self.sep+"@".join(map(str,self.word_suffissi[key]))+"\n"
	fd=open(self.radici_name,'w')
	fd.write(rtxt)
	fd.close()
	fd=open(self.suffissi_name,'w')

	fd.write(stxt)
	fd.close()

    # vedi manuale perché  a  re.sub può  essere  passata una  funzione
    # invece di una stringa che calcola il replacement
    def decidi_suffissi(self,parola,radice):
        if parola.word==radice: return([])
        suff=re.sub(radice.regexp,"",parola.word)
        return([suff])

    def add_radice(self,parola,radice):
        suff=self.decidi_suffissi(parola,radice)
        if not self.radici.has_key(radice):
            self.radici[radice]=[]
        self.radici[radice].append(parola.word)
        for s in suff:
            if not self.suffissi.has_key(s):
                self.suffissi[s]=[]
            self.suffissi[s].append(parola.word)
        if not self.word_radici.has_key(parola):
            self.word_radici[parola]=radice
            self.word_suffissi[parola]=suff
            return
        oldvals=self.word_radici[parola]
        oldsuff=self.word_suffissi[parola]
        self.word_radici[parola]=radice
        self.word_suffissi[parola]=suff
        if ( oldvals and oldvals!=radice ):
            if self.radici.has_key(oldvals):
                self.radici[oldvals].remove(parola.word)
                if not self.radici[oldvals]:
                    del(self.radici[oldvals])
        for s in oldsuff:
            if s in suff: continue
            if self.suffissi.has_key(s):
                self.suffissi[s].remove(parola.word)
                if not self.suffissi[s]:
                    del(self.suffissi[s])

    def cerca_radice(self,w):
        # sono radici tutte le radici e tutte le parole che non hanno radice
        if self.word_radici.has_key(w.word):
            if self.word_radici[w.word]:
                return(self.word_radici[w.word])
        for r in self.radici.keys():
            if r.re.match(w.word):
                self.add_radice(w,r)
                return(r)
        self.senza_radice.append(w)
        return("")

    def cerca(self,words):
        self.senza_radice=[]
	for k in self.keys(): 
	    self.__delitem__(k)
        for w in words:
            self[w.word]=w
            #print w.word
            radice=self.cerca_radice(w)
            if not radice: continue
            self.word_radici[w.word]=radice
            self.word_suffissi[w.word]=self.decidi_suffissi(w,radice)

    def print_latex(self,fd):
        fd.write("\\subsection{Radici}\n\n")
        fd.write("\\begin{itemize*}\n")
        for r in self.radici.keys():
            fd.write("\\item[] \\spzrl{"+r+"}\n")
            fd.write("\\begin{itemize*}\n")
            for w in self.radici[r]:
                self[w].print_item(fd,self.word_suffissi[w])
            fd.write("\\end{itemize*}\n")
        for w in self.senza_radice:
            if self.has_key(w):
                self[w].print_item(fd)
        fd.write("\\end{itemize*}\n\n")
        fd.write("\\subsection{Suffissi}\n\n")
        fd.write("\\begin{itemize*}\n")
        for r in self.suffissi.keys():
            fd.write("\\item[] \\spzrl{"+r+"}\n")
            fd.write("\\begin{itemize*}\n")
            for w in self.suffissi[r]:
                self[w].print_item(fd)
            fd.write("\\end{itemize*}\n")
        fd.write("\\end{itemize*}\n\n")
        
    def load(self): 
	if not self.radici_name: return
	if not self.suffissi_name: return
	if not os.path.exists(self.radici_name): return
	if not os.path.exists(self.suffissi_name): return
	self.clear()
	fd=open(self.radici_name,'r')
	for r in fd.readlines(): 
	    r=r.replace("\n","").strip()
	    if not r: continue
	    x=r.split(self.sep)
	    k=x[0].strip()
            if len(x)<=1:
                self.word_radici[k]=None
                continue
            rtxt=x[1].strip()
            if not rtxt:
                rad=None
            else:
                rad=Radice(rtxt)
            self.word_radici[k]=rad
            if not rad:
                continue
            if not self.radici.has_key(rad):
                self.radici[rad]=[]
            self.radici[rad].append(k)
	fd.close()

	fd=open(self.suffissi_name,'r')
	for r in fd.readlines(): 
	    r=r.replace("\n","").strip()
	    if not r: continue
	    x=r.split(self.sep)
	    k=x[0].strip()
            if len(x)<=1:
                self.word_suffissi[k]=[]
                continue
            suff=map(lambda y: y.strip(),x[1:])
            self.word_suffissi[k]=suff
            for s in suff:
                if not self.suffissi.has_key(s):
                    self.suffissi[s]=[]
                self.suffissi[s].append(k)
	fd.close()

