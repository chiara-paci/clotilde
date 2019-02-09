# -*- coding: utf-8 -*-

import gtk
import gtk.glade
import re
import cgi
import gobject
import os
import sys

from config import *
from GtkUtility import *
from VMenu  import MenuGlossario
from Glossario import VOttVariante,VoceOttomana
from Parola import Parola,ParSuffisso
from Suffissi import Suffisso
import utility

class VDivisioni:
    def show(self): self.main.show()
    def destroy_function(self,obj): gtk.main_quit()

    def __init__(self,glossario):
        self.glossario=glossario

        self.dic={}
        self.dic["on_mainWindow_destroy"]=self.destroy_function
        self.dic["on_tvWork_row_activated"]=self.cb_tvwork_row_activated

        self.mainxml=gtk.glade.XML(GLADES["divisioni"])
        self.mainxml.signal_autoconnect(self.dic)

        self.main=self.mainxml.get_widget("mainWindow")

	self.tvDivisioni=self.mainxml.get_widget("tvDivisioni")
	self.tvWork=self.mainxml.get_widget("tvWork")

        self.menu=MenuGlossario(self.mainxml)
        self.main.add_accel_group(self.menu.accel_group)
        self.menu.connect("file","quit",self.destroy_function)
        self.menu.connect("file","save",self.save)
        self.menu.connect("file","saveas",self.save_as)

        self.set_models()

    def save_as(self,obj):
        fname=get_filename_by_dialog()
        self.save_divisioni(fname)

    def save(self,obj):
        fname=self.glossario.suffissi.f_divisioni
        self.save_divisioni(fname)

    def save_divisioni(self,fname):
        for r in self.model_work:
            self.glossario.suffissi.predivisioni[r[0]]=r[1]
        fd=open(fname,'w')
        print "Opening "+fname
        self.glossario.suffissi.save_predivisioni(fd)
        fd.close()
        
        
    def set_models(self):
        self.model_divisioni=gtk.TreeStore(object,object,object)
        self.model_work=gtk.ListStore(str,object,object)

        self.tvDivisioni.set_model(self.model_divisioni)
        tvc=ParolaTVColumn("parola",0)
        self.tvDivisioni.append_column(tvc)
        tvc=VoceTVColumn("voce",1)
        self.tvDivisioni.append_column(tvc)
        tvc=ParolaTVColumn("suffisso",2)
        self.tvDivisioni.append_column(tvc)

        self.tvWork.set_model(self.model_work)
        tvc=TextTVColumn("suffisso",0)
        self.tvWork.append_column(tvc)
        tvc=ArrayTVColumnEditable("divisioni",1,self.model_work,"@")
        self.tvWork.append_column(tvc)
        
        divisioni=self.glossario.suffissi.get_divisioni()

        print divisioni
        
        def myappend(row):
            s=row[0]
            d=row[1]
            t=[]
            if s:
                for (p,v) in row[2]:
                    i=self.model_divisioni.append(None,[p,v,ParSuffisso(s)])
                    t.append(i)
                self.model_work.append([s,d,t])
            else:
                i=self.model_divisioni.append(None,["SENZA",None,None])
                for (p,v) in row[2]:
                    self.model_divisioni.append(i,[p,v,None])

        map(myappend,divisioni)

        
    def cb_tvwork_row_activated(self,tv,path,column):
        iter=self.model_work.get_iter(path)
        obj=self.model_work.get_value(iter,2)
        treesel=self.tvDivisioni.get_selection()
        treesel.set_mode(gtk.SELECTION_MULTIPLE)
        treesel.unselect_all()
        for i in obj:
            treesel.select_iter(i)
