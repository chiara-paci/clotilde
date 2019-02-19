# -*- coding: utf-8 -*-

import gtk
import gtk.glade
import re
import cgi
import gobject
import os
import sys

from config import *
import utility

def get_filename_by_dialog(style="filesaver",title=""):
    wdxml=gtk.glade.XML(GLADES[style])
    wd=wdxml.get_widget("dialogMain")
    lTit=wdxml.get_widget("labelTitle")
    lTit.set_label(title)
    if style=="filesaver":
	wd.set_action(gtk.FILE_CHOOSER_ACTION_SAVE)
	wd.set_do_overwrite_confirmation(True)
    if style=="diropener":
	wd.set_action(gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER)
	#wd.set_do_overwrite_confirmation(True)
	#wd.set_property("do-overwrite-confirmation",True)
    wd.show()
    res=wd.run()
    if res==0:
	wd.hide()
	return("")
    fname=wd.get_filename()
    wd.hide()
    if style=="filechooser": return(fname)
    if style=="diropener": return(fname)
    if not os.path.exists(fname): return(fname)
    wdxml=gtk.glade.XML(GLADES["confirmation"])
    wd=wdxml.get_widget("dialogMain")
    label=wdxml.get_widget("labelMessage")
    label.set_label("File "+fname+" already exists: overwrite?")
    wd.show()
    res=wd.run()
    #sì voglio veramente
    if res==0:
	wd.hide()
	return(fname)
    #ok ho sbagliato
    wd.hide()
    return(get_filename_by_dialog(style=style,title=title))


def get_filename_categoria(categorie,active=0):
    wdxml=gtk.glade.XML(GLADES["filesaver-categorie"])
    wd=wdxml.get_widget("dialogMain")
    wd.set_current_folder_uri(REPORT_FOLDER)
    cCat=wdxml.get_widget("comboCategorie")
    model=gtk.ListStore(str)
    map(lambda x: model.append([x]),categorie)
    cCat.set_model(model)
    cell = gtk.CellRendererText()
    cCat.pack_start(cell, True)
    cCat.add_attribute(cell, 'text', 0)
    cCat.set_active(active)
    wd.set_action(gtk.FILE_CHOOSER_ACTION_SAVE)
    wd.set_do_overwrite_confirmation(True)
    wd.show()
    res=wd.run()
    if res==0:
	wd.hide()
	return("")
    fname=wd.get_filename()
    active=cCat.get_active()
    wd.hide()
    if not os.path.exists(fname): return((fname,active))
    wdxml=gtk.glade.XML(GLADES["confirmation"])
    wd=wdxml.get_widget("dialogMain")
    label=wdxml.get_widget("labelMessage")
    label.set_label("File "+fname+" already exists: overwrite?")
    wd.show()
    res=wd.run()
    #sì voglio veramente
    if res==0:
	wd.hide()
	return((fname,active))
    #ok ho sbagliato
    wd.hide()
    return(get_filename_by_dialog(categorie,active=active))

VCOLORI={ "nonorigine": (0,1,1),
          "nonref": (1,0,0),
          "nonrefpron": (1,0,0),
          "lowref": (1,1,0.5),
          "lowrefpron": (1,0.5,1),
          "nosignificato": (1,0,0),
          "sologlossario": (0.9,0.9,0.9),
          "solodoc": (1,0,0) }

VARABO=0
VTRASCRIZIONE=1

class TextTVColumn(gtk.TreeViewColumn):
    def __init__(self,titolo,col_id,col_back=None):
        gtk.TreeViewColumn.__init__(self,titolo)
        c=gtk.CellRendererText()
        self.pack_start(c,True)
        if col_back!=None:
            self.set_attributes(c,text=col_id,background=col_back)
        else:
            self.set_attributes(c,text=col_id)
        self.set_resizable(True)
        self.set_reorderable(True)
        self.set_sort_column_id(col_id)

class TextTVColumnEditable(gtk.TreeViewColumn):
    def __init__(self,titolo,col_id,model):
        gtk.TreeViewColumn.__init__(self,titolo)
        c=gtk.CellRendererText()
        self.pack_start(c,True)
        self.set_attributes(c,text=col_id)
        self.set_resizable(True)
        self.set_reorderable(True)
        self.set_sort_column_id(col_id)
        c.set_property("editable",True)
        c.connect("edited",self.edited_cb)
        self.model=model
        self.col_id=col_id

    def edited_cb(self,cell,path,new_text):
	iter=self.model.get_iter(path)
        t=self.model.get_column_type(self.col_id)
        if t==gobject.TYPE_INT: new_text=int(new_text)
        self.model.set_value(iter,self.col_id,new_text)

class ArrayTVColumnEditable(gtk.TreeViewColumn):
    def __init__(self,titolo,col_id,model,sep):
        gtk.TreeViewColumn.__init__(self,titolo)
        c=gtk.CellRendererText()
        self.pack_start(c,True)
        self.set_cell_data_func(c,self.set_text)
        self.set_resizable(True)
        self.set_reorderable(True)
        self.set_sort_column_id(col_id)
        c.set_property("editable",True)
        c.connect("edited",self.edited_cb)
        self.model=model
        self.col_id=col_id
        self.sep=sep

    def edited_cb(self,cell,path,new_text):
        t=new_text.split("@")
	iter=self.model.get_iter(path)
        self.model.set_value(iter,self.col_id,t)

    def set_text(self,column,cell_renderer, model, iter):
	L=model.get_value(iter,self.col_id)
        text=self.sep.join(L)
	cell_renderer.set_property('text',text)

def calcola_sostegno_hamza(n,target):
    if n==0: return("A")
    if n==1:
        prec=target[0]
    elif target[n-2] in SWITCHES:
        prec=target[n-2:n]
    else:
        prec=target[n-1]
    if n==len(target)-1:
        succ=""
    elif n==len(target)-2:
        succ=target[len(target)-1]
    elif target[n+1] in SWITCHES:
        succ=target[n+1:n+3]
    else:
        succ=target[n+1]
    if ( (prec in HARAKAT[HARAKAT_IND["i"]])
         or (succ in HARAKAT[HARAKAT_IND["i"]]) ): return("y")
    if ( (prec in HARAKAT[HARAKAT_IND["u"]])
         or (succ in HARAKAT[HARAKAT_IND["u"]]) ): return("w")
    return("A")

def get_conversione(codifica,trascr_id):
    text=u""
    n=0
    if ( (not codifica) or (codifica[0]=="\\") ): 
        #cell_renderer.set_property('text',"")
        return("")
    while n<len(codifica):
        ch=codifica[n]
        add=0
        if ch in IGNORA and not ARAB_CONVERSIONE.has_key(ch):
            n+=1
            continue
        if ch in SWITCHES:
            ch=codifica[n:n+2]
            add=1
        if not ARAB_CONVERSIONE.has_key(ch):
            n+=add+1
            continue
        if trascr_id==VARABO and ch=="'":
            base=calcola_sostegno_hamza(n,codifica)
            if base=="w":
                ucode=[0x0624]
            elif base=="y":
                ucode=[0x626]
            else:
                ucode=[0x0672]
            text+=list_to_unicode(ucode)
            n+=1+add
            continue
        tch=ARAB_CONVERSIONE[ch][trascr_id]
        if trascr_id==VARABO and VARIANTI.has_key(ch):
            if ( (n+add==len(codifica)-1) and (n==0) ):
                if VARIANTI[ch][0]: tch=VARIANTI[ch][0]
            elif ( (n==0) or ( (n>=1) and (codifica[n-1]=="-") )
                   or ( (n>=2) and (codifica[n-2:n]=="||")) ):
                if VARIANTI[ch][1]: tch=VARIANTI[ch][1]
                    
            elif n+add==len(codifica)-1:
                if VARIANTI[ch][3]: tch=VARIANTI[ch][3]
            else:
                if VARIANTI[ch][2]: tch=VARIANTI[ch][2]
        if type(tch)==list:
            text+=list_to_unicode(tch)
        else:
            text+=tch
        n+=1+add
    return(text)


class TransTVColumn(gtk.TreeViewColumn):
    def __init__(self,titolo,col_id,trascr_id,col_back=None):
        gtk.TreeViewColumn.__init__(self,titolo)
	self.col_id=col_id
        self.trascr_id=trascr_id
        c=gtk.CellRendererText()
        self.pack_start(c,True)
        if col_back!=None:
            self.set_attributes(c,background=col_back)
        self.set_cell_data_func(c,self.set_text)
	
    def set_text(self,column,cell_renderer, model, iter):
	codifica=model.get_value(iter,self.col_id)
        text=get_conversione(codifica,self.trascr_id)
	cell_renderer.set_property('text',text)


class VoceTVColumn(gtk.TreeViewColumn):
    def __init__(self,titolo,col_id):
        gtk.TreeViewColumn.__init__(self,titolo)
	self.col_id=col_id
        c=gtk.CellRendererText()
        self.pack_start(c,True)
        self.set_cell_data_func(c,self.set_text)
        c=gtk.CellRendererText()
        self.pack_start(c,True)
        self.set_cell_data_func(c,self.set_trans,VTRASCRIZIONE)
        c=gtk.CellRendererText()
        self.pack_start(c,True)
        self.set_cell_data_func(c,self.set_trans,VARABO)
        self.set_resizable(True)
        self.set_reorderable(True)
        self.set_sort_column_id(col_id)
	
    def set_trans(self,column,cell_renderer, model, iter,trans_id):
	codifica=model.get_value(iter,self.col_id)
        if not codifica:
            cell_renderer.set_property('text','')
            return
        if type(codifica)==str:
            cell_renderer.set_property('text','')
            return
        text=get_conversione(codifica.voce,trans_id)
	cell_renderer.set_property('text',text)

    def set_text(self,column,cell_renderer, model, iter):
	codifica=model.get_value(iter,self.col_id)
        if not codifica:
            cell_renderer.set_property('text','')
            return
        if type(codifica)==str:
            text=codifica
        else:
            text=codifica.voce
	cell_renderer.set_property('text',text)

class ParolaTVColumn(gtk.TreeViewColumn):
    def __init__(self,titolo,col_id):
        gtk.TreeViewColumn.__init__(self,titolo)
	self.col_id=col_id
        c=gtk.CellRendererText()
        self.pack_start(c,True)
        self.set_cell_data_func(c,self.set_text)
        c=gtk.CellRendererText()
        self.pack_start(c,True)
        self.set_cell_data_func(c,self.set_trans,VTRASCRIZIONE)
        c=gtk.CellRendererText()
        self.pack_start(c,True)
        self.set_cell_data_func(c,self.set_trans,VARABO)
        self.set_resizable(True)
        self.set_reorderable(True)
        self.set_sort_column_id(col_id)
	
    def set_text(self,column,cell_renderer, model, iter):
	codifica=model.get_value(iter,self.col_id)
        if not codifica:
            cell_renderer.set_property('text','')
            return
        if type(codifica)==str:
            text=codifica
        else:
            text=codifica.word
	cell_renderer.set_property('text',text)

    def set_trans(self,column,cell_renderer, model, iter,trans_id):
	codifica=model.get_value(iter,self.col_id)
        if not codifica:
            cell_renderer.set_property('text','')
            return
        if type(codifica)==str:
            cell_renderer.set_property('text','')
            return
        text=get_conversione(codifica.word,trans_id)
	cell_renderer.set_property('text',text)


class TreTransTVColumn(gtk.TreeViewColumn):
    def __init__(self,titolo,col_id,editable=False,model=None):
        gtk.TreeViewColumn.__init__(self,titolo)
        self.model=model
	self.col_id=col_id

        c=gtk.CellRendererText()
        self.pack_start(c,True)
        self.set_attributes(c,text=col_id)
        if editable:
            c.set_property("editable",True)
            c.connect("edited",self.edited_cb)
        c=gtk.CellRendererText()
        self.pack_start(c,True)
        self.set_cell_data_func(c,self.set_trans,VTRASCRIZIONE)
        c=gtk.CellRendererText()
        self.pack_start(c,True)
        self.set_cell_data_func(c,self.set_trans,VARABO)
        self.set_resizable(True)
        self.set_reorderable(True)
        self.set_sort_column_id(col_id)
	
    def set_trans(self,column,cell_renderer, model, iter,trans_id):
	text=model.get_value(iter,self.col_id)
        text=get_conversione(text,trans_id)
	cell_renderer.set_property('text',text)

    def edited_cb(self,cell,path,new_text):
	iter=self.model.get_iter(path)
        t=self.model.get_column_type(self.col_id)
        self.model.set_value(iter,self.col_id,new_text)

class IntTVColumn(gtk.TreeViewColumn):
    def __init__(self,titolo,col_id):
        gtk.TreeViewColumn.__init__(self,titolo)
	self.col_id=col_id
        c=gtk.CellRendererText()
        self.pack_start(c,True)
        self.set_cell_data_func(c,self.set_text)
	
    def set_text(self,column,cell_renderer, model, iter):
	val=model.get_value(iter,self.col_id)
	cell_renderer.set_property('text',str(val))

class PercTVColumn(gtk.TreeViewColumn):
    def __init__(self,titolo,col_id):
        gtk.TreeViewColumn.__init__(self,titolo)
	self.col_id=col_id
        c=gtk.CellRendererText()
        self.pack_start(c,True)
        self.set_cell_data_func(c,self.set_text,0)
        c=gtk.CellRendererText()
        self.pack_start(c,True)
        self.set_cell_data_func(c,self.set_perc,0)
        c=gtk.CellRendererText()
        self.pack_start(c,True)
        self.set_cell_data_func(c,self.set_text,1)
        c=gtk.CellRendererText()
        self.pack_start(c,True)
        self.set_cell_data_func(c,self.set_perc,1)
	
    def set_text(self,column,cell_renderer, model, iter,n):
	row=model.get_value(iter,1)
        val=row[self.col_id][n]
	cell_renderer.set_property('text',str(val))

    def set_perc(self,column,cell_renderer, model, iter,n):
        row=model.get_value(iter,1)
	v=row[self.col_id][n]
        try:
            tot=reduce(lambda x,y: x+y,map(lambda z:z[n],row))
        except TypeError, e:
            print row
            sys.exit()
        if tot:
            val=100.0*v/tot
        else:
            val=0
	cell_renderer.set_property('text',"%2.2f %%" % val)

class TotTVColumn(gtk.TreeViewColumn):
    def __init__(self,titolo):
        gtk.TreeViewColumn.__init__(self,titolo)
        c=gtk.CellRendererText()
        self.pack_start(c,True)
        self.set_cell_data_func(c,self.set_text,0)
        c=gtk.CellRendererText()
        self.pack_start(c,True)
        self.set_cell_data_func(c,self.set_text,1)
	
    def set_text(self,column,cell_renderer,model,iter,n):
        row=model.get_value(iter,1)
        #val=0
        val=reduce(lambda x,y: x+y,map(lambda z:z[n],row))
        #val=reduce(lambda x,y: x[n]+y[n],row)
        #for c in self.col_ids:
        #    val+=
	cell_renderer.set_property('text',str(val))


class StockElement:
    def __init__(self,id,fname,label,mask,char):
	self.id=id
	self.fname=fname
	self.label=label
	self.mask=mask
	self.char=char

    def get_iconset(self,imgdir):
	img=gtk.Image()
	img.set_from_file(imgdir+"/"+self.fname)
	print imgdir+"/"+self.fname
	pbuf=img.get_pixbuf()
	return(gtk.IconSet(pbuf))

    def get_tuple(self,tdomain):
	t=(self.id,self.label,self.mask,
	   gtk.gdk.keyval_from_name(self.char),tdomain)
	return(t)

class StockElementControl(StockElement):
    def __init__(self,id,fname,label,char):
	StockElement.__init__(self,id,fname,label,
			      gtk.gdk.CONTROL_MASK,char)

class StockElementControlShift(StockElement):
    def __init__(self,id,fname,label,char):
	StockElement.__init__(self,id,fname,label,
			      gtk.gdk.CONTROL_MASK | gtk.gdk.SHIFT_MASK,char)

class StockElementMod1(StockElement):
    def __init__(self,id,fname,label,char):
	StockElement.__init__(self,id,fname,label,gtk.gdk.MOD1_MASK,char)

class GStockFactory:
    def __init__(self,tdomain,imgdir):
	self.tdomain=tdomain
	self.imgdir=imgdir
	self.ifactory=gtk.IconFactory()

    def add_default(self): self.ifactory.add_default()
    
    def append(self,elem):
	self.ifactory.add(elem.id,elem.get_iconset(self.imgdir))
	gtk.stock_add([elem.get_tuple(self.tdomain)])

STOCK_FACTORY=GStockFactory("analisi",IMGDIR)
STOCK_FACTORY.append(StockElementControlShift("glossario-export",
                                              "tex.png",
                                              "Export",'X'))
STOCK_FACTORY.append(StockElementControlShift("glossario-export-matrix",
                                              "tex.png",
                                              "Export Matrix",'X'))
STOCK_FACTORY.append(StockElementControlShift("glossario-export-statistiche",
                                              "tex.png",
                                              "Export Statistiche",'X'))
STOCK_FACTORY.append(StockElementControlShift("glossario-categorie",
                                              "tex.png",
                                              "Per categorie",'C'))
STOCK_FACTORY.add_default()
