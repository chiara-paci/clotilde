# -*- coding: utf-8 -*-

from config import *
from Voci import decidi_colore

class GCategorizzatore(object):
    def __init__(self,glossario,label,title):
        self.glossario=glossario
        self.label=label
        self.title=title

    def filtro(self,x): return(False)

    def get_list(self):
        L=filter(self.filtro,self.glossario.get_all())
        return(L)

    def print_tex_mini(self,fd):
        for voce in self.get_list():
            (color,bullet)=decidi_colore(voce)
            if color=="colorsologlossario":
                continue
            voce.print_item_base_cat(fd)

    def print_tex(self,fd):
        for voce in self.get_list():
            (color,bullet)=decidi_colore(voce)
            if color=="colorsologlossario":
                continue
            voce.print_item_cat(fd)
            if color: fd.write("Color: "+color+"\n")
            if bullet: fd.write("Bullet: "+bullet+"\n")
            if not voce.cosa_guardare:
                fd.write("\n")
                continue
            fd.write("Contesti:\n")
            fd.write("\\begin{subvocedue}\n")
            for (rmin,cmin,rmax,cmax,T) in self.glossario.get_contesti(voce):
                if rmin==rmax:
                    label="(riga "+str(rmin+1)+")"
                else:
                    label="(righe "+str(rmin+1)+"-"+str(rmax+1)+")"
                print label,voce.word
                fd.write("\\item["+label+"] ")
                fd.write(spzrl(T)+"\n")
            fd.write("\\end{subvocedue}\n")
            fd.write("\n")

    def __nonzero__(self):
        print self.label, self.glossario.abbr_valide
        return(self.label in self.glossario.abbr_valide)

class GCatCategoria(GCategorizzatore):
    def __init__(self,glossario,categoria):
        GCategorizzatore.__init__(self,glossario,categoria,
                                  "Categoria: "+TUTTE_CATEGORIE[categoria])

    def filtro(self,x):
        return(self.label in x.categorie)

class GCatNoCat(GCategorizzatore):
    def __init__(self,glossario):
        GCategorizzatore.__init__(self,glossario,"no-cat",
                                  "Categoria: NO")
    
    def filtro(self,x):
        return((not bool(x.categorie)))

    def __nonzero__(self):
        return(True)

class GCatNoOrig(GCategorizzatore):
    def __init__(self,glossario):
        GCategorizzatore.__init__(self,glossario,"no-orig",
                                  "Origine: NO")
    
    def filtro(self,x):
        return((not bool(x.origine)))

    def __nonzero__(self):
        return(True)

class GCatOrigine(GCategorizzatore):
    def __init__(self,glossario,origine):
        GCategorizzatore.__init__(self,glossario,origine,
                                  "Origine: "+ORIGINI[origine])

    def filtro(self,x):
        if not x.origine: return(False)
        if ("np" in x.categorie) and (len(x.categorie)==1):
            return(False)
        if x.origine[-1]=="?":
            return(x.origine[:-1]==self.label)
        return(x.origine==self.label)

class GCatOrigineNot(GCatOrigine):
    def __init__(self,glossario,origine):
        GCategorizzatore.__init__(self,glossario,origine,
                                  "Not Origine: "+ORIGINI[origine])

    def filtro(self,x):
        return(not GCatOrigine.filtro(self,x))

class GCatOrigineCategoria(GCategorizzatore):
    def __init__(self,glossario,origine,categoria):
        t=ORIGINI[origine]+"-"+TUTTE_CATEGORIE[categoria].lower()
        GCategorizzatore.__init__(self,glossario,origine+":"+categoria,t)
        self.label_origine=origine
        self.label_categoria=categoria

    def filtro(self,x):
        if not x.origine: return(False)
        if ("np" in x.categorie) and (len(x.categorie)==1):
            return(False)
        orig=x.origine
        if orig[-1]=="?": orig=orig[:-1]
        return( (orig==self.label_origine) and (self.label_categoria in x.categorie) )

class GCatMarbuta(GCategorizzatore):
    def __init__(self,glossario):
        GCategorizzatore.__init__(self,glossario,"marbuta","Ta Marbuta")
        
    def filtro(self,x):
        if x.origine.lower() not in ORIGINI_ARABE:
            return(False)
        if x.voce[-1] in [ "T", "H" ]: return(True)
        if x.voce[-1]!="t": return(False)
        if x.voce[-2:] in [ "_t", ".t" ]: return(False)
        return(True)

    def __nonzero__(self):
        return(True)

