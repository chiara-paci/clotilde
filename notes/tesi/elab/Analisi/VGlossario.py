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
from VMenu  import MenuVGlossario
from Voci   import VOttVariante,VoceOttomana,decidi_colore
from Parola import Parola,ParSuffisso
from Suffissi import Suffisso
import utility

class VGlossario:
    def show(self): self.main.show()
    def destroy_function(self,obj): gtk.main_quit()

    def __init__(self,glossario):
        self.glossario=glossario

        self.tvindexkeys=[ "tvIndex", "tvIndexGrammaticali",
                           "tvIndexCategorie", "tvIndexNuove",
                           "tvIndexTabelle",
                           "tvIndexSuffissi",
                           "tvIndexFormeArabe" ]
        self.dic={}
        self.dic["on_mainWindow_destroy"]=self.destroy_function

        for k in self.tvindexkeys:
            self.dic["on_"+k+"_row_activated"]=self.cb_tvindex_row_activated

        self.dic["on_buttonReference_clicked"]=self.cb_buttonreference_clicked
        self.dic["on_buttonVReference_clicked"]=self.cb_buttonvreference_clicked
        self.dic["on_buttonApply_clicked"]=self.cb_buttonapply_clicked
        self.dic["on_buttonAddSub_clicked"]=self.cb_buttonaddsub_clicked
        self.dic["on_buttonAddComposto_clicked"]=self.cb_buttonaddcomposto_clicked
        self.dic["on_buttonAddCompPrep_clicked"]=self.cb_buttonaddcompprep_clicked
        self.dic["on_buttonDelSub_clicked"]=self.cb_buttondelsub_clicked
        self.dic["on_buttonDelVoce_clicked"]=self.cb_buttondelvoce_clicked
        self.dic["on_buttonRefPronuncia_clicked"]=self.cb_buttonrefpronuncia_clicked
        self.dic["on_entryVoce_changed"]=self.cb_entryvoce_changed
        self.dic["on_buttonVApply_clicked"]=self.cb_buttonvapply_clicked
        self.dic["on_entryVVoce_changed"]=self.cb_entryvvoce_changed

        self.dic["on_entrySfVoce_changed"]=self.cb_entrysfvoce_changed
        self.dic["on_buttonSfApply_clicked"]=self.cb_buttonsfapply_clicked
        self.dic["on_buttonSfDelete_clicked"]=self.cb_buttonsfdelete_clicked
        self.dic["on_buttonSfAddAllomorfo_clicked"]=self.cb_buttonsfaddallomorfo_clicked
        self.dic["on_buttonSfRemoveAllomorfo_clicked"]=self.cb_buttonsfremoveallomorfo_clicked

        self.dic["on_buttonPInGlossario_clicked"]=self.cb_buttonpinglossario_clicked
        self.dic["on_entryPVoce_changed"]=self.cb_entrypvoce_changed
        self.dic["on_buttonSInGlossario_clicked"]=self.cb_buttonsinglossario_clicked
        self.dic["on_entrySVoce_changed"]=self.cb_entrysvoce_changed

        self.mainxml=gtk.glade.XML(GLADES["glossario"])
        self.mainxml.signal_autoconnect(self.dic)

        self.main=self.mainxml.get_widget("mainWindow")
	self.frameAggiunte=self.mainxml.get_widget("frameAggiunte")
	self.nbMain=self.mainxml.get_widget("nbMain")

        self.tvIndex={}
        for k in self.tvindexkeys:
            self.tvIndex[k]=self.mainxml.get_widget(k)


	self.tvDocumento=self.mainxml.get_widget("tvDocumento")
	self.tvSubvoci=self.mainxml.get_widget("tvSubvoci")
	self.tvVarianti=self.mainxml.get_widget("tvVarianti")
	self.tvContesti=self.mainxml.get_widget("tvContesti")
	self.tvAlfabeto=self.mainxml.get_widget("tvAlfabeto")
	self.tvCategorie=self.mainxml.get_widget("tvCategorie")
	#self.tvElencoMain=self.mainxml.get_widget("tvElencoMain")

	self.buttonAddSub=self.mainxml.get_widget("buttonAddSub")
	self.buttonAddComposto=self.mainxml.get_widget("buttonAddComposto")
	self.buttonAddCompPrep=self.mainxml.get_widget("buttonAddCompPrep")
	self.buttonDelSub=self.mainxml.get_widget("buttonDelSub")
	self.buttonDelVoce=self.mainxml.get_widget("buttonDelVoce")

        self.entrySfVoce=self.mainxml.get_widget("entrySfVoce")
        self.entrySfCategoria=self.mainxml.get_widget("entrySfCategoria")
        self.entrySfClasse=self.mainxml.get_widget("entrySfClasse")
        self.entrySfInput=self.mainxml.get_widget("entrySfInput")
        self.entrySfOutput=self.mainxml.get_widget("entrySfOutput")
        self.entrySfPronuncia=self.mainxml.get_widget("entrySfPronuncia")
        self.labelSfArabo=self.mainxml.get_widget("labelSfArabo")
        self.labelSfTrascrizione=self.mainxml.get_widget("labelSfTrascrizione")
        self.labelSfStatus=self.mainxml.get_widget("labelSfStatus")
        self.eventSfStatus=self.mainxml.get_widget("eventSfStatus")
        self.textviewSfSignificato=self.mainxml.get_widget("textviewSfSignificato")
        self.textviewSfNote=self.mainxml.get_widget("textviewSfNote")
        self.textviewSfReference=self.mainxml.get_widget("textviewSfReference")
        self.textviewSfRefPronuncia=self.mainxml.get_widget("textviewSfRefPronuncia")
        self.entrySfOrigine=self.mainxml.get_widget("entrySfOrigine")
        self.comboSfReference=self.mainxml.get_widget("comboSfReference")
        self.comboSfRefPronuncia=self.mainxml.get_widget("comboSfRefPronuncia")
        self.entrySfReference=self.mainxml.get_widget("entrySfReference")
        self.entrySfRefPronuncia=self.mainxml.get_widget("entrySfRefPronuncia")
        self.checkSfVerificare=self.mainxml.get_widget("checkVerificare")
        self.tvSfParole=self.mainxml.get_widget("tvSfParole")
        self.tvSfAllomorfi=self.mainxml.get_widget("tvSfAllomorfi")
        self.tvSMatches=self.mainxml.get_widget("tvSMatches")

        self.entryVoce=self.mainxml.get_widget("entryVoce")
        self.entryPronuncia=self.mainxml.get_widget("entryPronuncia")
        self.entryGuardare=self.mainxml.get_widget("entryGuardare")
        self.labelIndice=self.mainxml.get_widget("labelIndice")
        self.labelArabo=self.mainxml.get_widget("labelArabo")
        self.labelTrascrizione=self.mainxml.get_widget("labelTrascrizione")
        self.labelStatus=self.mainxml.get_widget("labelStatus")
        self.eventStatus=self.mainxml.get_widget("eventStatus")
        self.textviewSignificato=self.mainxml.get_widget("textviewSignificato")
        self.textviewNote=self.mainxml.get_widget("textviewNote")
        self.textviewReference=self.mainxml.get_widget("textviewReference")
        self.textviewRefPronuncia=self.mainxml.get_widget("textviewRefPronuncia")
        self.entryCategoria=self.mainxml.get_widget("entryCategoria")
        self.entryOrigine=self.mainxml.get_widget("entryOrigine")
        self.comboReference=self.mainxml.get_widget("comboReference")
        self.comboRefPronuncia=self.mainxml.get_widget("comboRefPronuncia")
        self.entryReference=self.mainxml.get_widget("entryReference")
        self.entryRefPronuncia=self.mainxml.get_widget("entryRefPronuncia")

        self.entryVOccasione=self.mainxml.get_widget("entryVOccasione")

        self.labelVStatus=self.mainxml.get_widget("labelVStatus")
        self.eventVStatus=self.mainxml.get_widget("eventVStatus")
        self.labelVArabo=self.mainxml.get_widget("labelVArabo")
        self.labelVTrascrizione=self.mainxml.get_widget("labelVTrascrizione")
        self.entryVVoce=self.mainxml.get_widget("entryVVoce")
        self.entryVPronuncia=self.mainxml.get_widget("entryVPronuncia")

        self.labelPStatus=self.mainxml.get_widget("labelPStatus")
        self.eventPStatus=self.mainxml.get_widget("eventPStatus")
        self.labelPArabo=self.mainxml.get_widget("labelPArabo")
        self.labelPTrascrizione=self.mainxml.get_widget("labelPTrascrizione")
        self.entryPVoce=self.mainxml.get_widget("entryPVoce")
        self.entryPPronuncia=self.mainxml.get_widget("entryPPronuncia")

        self.labelSStatus=self.mainxml.get_widget("labelSStatus")
        self.eventSStatus=self.mainxml.get_widget("eventSStatus")
        self.labelSArabo=self.mainxml.get_widget("labelSArabo")
        self.labelSTrascrizione=self.mainxml.get_widget("labelSTrascrizione")
        self.entrySVoce=self.mainxml.get_widget("entrySVoce")
        self.entrySPronuncia=self.mainxml.get_widget("entrySPronuncia")

        self.textviewVReference=self.mainxml.get_widget("textviewVReference")
        self.textviewVRefPronuncia=self.mainxml.get_widget("textviewVRefPronuncia")
        self.comboVReference=self.mainxml.get_widget("comboVReference")
        self.comboVRefPronuncia=self.mainxml.get_widget("comboVRefPronuncia")
        self.entryVReference=self.mainxml.get_widget("entryVReference")
        self.entryVRefPronuncia=self.mainxml.get_widget("entryVRefPronuncia")

        self.checkVerificare=self.mainxml.get_widget("checkVerificare")

        self.tvStatistiche=self.mainxml.get_widget("tvStatistiche")

        self.menu=MenuVGlossario(self.mainxml)
        self.main.add_accel_group(self.menu.accel_group)
        self.menu.connect("file","quit",self.destroy_function)
        self.menu.connect("file","save",self.save)
        self.menu.connect("file","saveas",self.save_as)
        self.menu.connect("glossario","export",self.menu_glossario_export)
        self.menu.connect("glossario","export_matrix",
                          self.menu_glossario_export_matrix)
        self.menu.connect("glossario","export_statistiche",
                          self.menu_glossario_export_statistiche)
        self.menu.connect("glossario","tex_categorie",
                          self.menu_glossario_tex_categorie)

        self.pagine={ "alfabeto": 1,
                      "voce": 0,
                      "variante": 2,
                      "categoria": 5,
                      "statistiche": 6,
                      "parsuffisso": 7,
                      "suffisso": 3,
                      "parola": 4 }

        self.pagine["subvoce"]=self.pagine["voce"]
        self.pagine["alternativa"]=self.pagine["voce"]

        self.nbMain.set_current_page(self.pagine["alfabeto"])
        self.current=None
        self.current_iter=None
        self.current_subiter=None
        self.set_models()

    def save_as(self,obj):
        fname=get_filename_by_dialog()
        fd=open(fname,'w')
        print "Opening "+fname
        self.glossario.save(fd)
        fd.close()
        
    def save(self,obj):
        fname=self.glossario.finput["glossario"]
        fd=open(fname,'w')
        print "Opening "+fname
        self.glossario.save(fd)
        fd.close()
        #fname=self.glossario.finput["suffissi"]
        #fd=open(fname,'w')
        #print "Opening "+fname
        #self.glossario.suffissi.save(fd)
        #fd.close()
        
    def set_models(self):
        self.set_alfabeto()
        self.set_statistiche()
        self.set_index()

        model=gtk.ListStore(str,bool)
        model.append(["sec/sec:turconomi",False])
        model.append(["tab/tab:nomiturchi",False])
        model.append(["tab/tab:aggettiviturchi",False])
        model.append(["sec/sec:turcoverbi",False])
        model.append(["sec/sec:verbipersiani",False])
        model.append(["sec/sec:nomipersiani",False])
        model.append(["tab/tab:nomipersiani",False])
        model.append(["sec/sec:aggettivipersiani",False])
        model.append(["tab/tab:verbiturchi",False])
        model.append(["bib/steingass1992",True])
        model.append(["bib/meninski1680d1",True])
        model.append(["bib/meninski1680d2",True])
        model.append(["bib/meninski1680d3",True])
        model.append(["bib/meninski1680g",True])
        model.append(["bib/kiefferbianchi18351",True])
        model.append(["bib/kiefferbianchi18352",True])
        model.append(["bib/redhouse1997",True])
        model.append(["bib/timurtas1999",True])
        model.append(["tab/tab:nomiturchi",False])
        model.append(["sec/sec:turcoverbiausiliari",False])
        cell = gtk.CellRendererText()
        self.comboReference.pack_start(cell, True)
        self.comboReference.add_attribute(cell, 'text', 0)
        self.comboReference.set_model(model)
        cell = gtk.CellRendererText()
        self.comboRefPronuncia.pack_start(cell, True)
        self.comboRefPronuncia.add_attribute(cell, 'text', 0)
        self.comboRefPronuncia.set_model(model)

        self.comboReference.set_active(0)
        self.comboRefPronuncia.set_active(1)

        cell = gtk.CellRendererText()
        self.comboVReference.pack_start(cell, True)
        self.comboVReference.add_attribute(cell, 'text', 0)
        self.comboVReference.set_model(model)
        cell = gtk.CellRendererText()
        self.comboVRefPronuncia.pack_start(cell, True)
        self.comboVRefPronuncia.add_attribute(cell, 'text', 0)
        self.comboVRefPronuncia.set_model(model)

        self.comboVReference.set_active(1)

        cell = gtk.CellRendererText()
        self.comboSfReference.pack_start(cell, True)
        self.comboSfReference.add_attribute(cell, 'text', 0)
        self.comboSfReference.set_model(model)
        cell = gtk.CellRendererText()
        self.comboSfRefPronuncia.pack_start(cell, True)
        self.comboSfRefPronuncia.add_attribute(cell, 'text', 0)
        self.comboSfRefPronuncia.set_model(model)
        self.comboSfReference.set_active(3)

        self.model_categorie=gtk.ListStore(str,object,str,str)
        self.tvCategorie.set_model(self.model_categorie)
        tvc=TransTVColumn("arabo",0,VARABO)
        self.tvCategorie.append_column(tvc)
        tvc=TransTVColumn("trascrizione",0,VTRASCRIZIONE)
        self.tvCategorie.append_column(tvc)
        tvc=TextTVColumn("cat.",2)
        self.tvCategorie.append_column(tvc)
        tvc=TextTVColumn("orig.",3)
        self.tvCategorie.append_column(tvc)
        tvc=TextTVColumn("arabtex",0)
        self.tvCategorie.append_column(tvc)

        self.model_sfparole=gtk.ListStore(str,str)
        self.col_sfparole={ "match": 0, "righe": 1 }

        self.tvSfParole.set_model(self.model_sfparole)
        tvc=TransTVColumn("arabo",self.col_sfparole["match"],VARABO)
        self.tvSfParole.append_column(tvc)
        tvc=TransTVColumn("trascrizione",self.col_sfparole["match"],VTRASCRIZIONE)
        self.tvSfParole.append_column(tvc)
        tvc=TextTVColumn("righe",self.col_sfparole["righe"])
        self.tvSfParole.append_column(tvc)
        tvc=TextTVColumn("arabtex",self.col_sfparole["match"])
        self.tvSfParole.append_column(tvc)

        self.model_sfallomorfi=gtk.ListStore(str)
        self.tvSfAllomorfi.set_model(self.model_sfallomorfi)
        tvc=TransTVColumn("arabo",0,VARABO)
        self.tvSfAllomorfi.append_column(tvc)
        tvc=TransTVColumn("trascrizione",0,VTRASCRIZIONE)
        self.tvSfAllomorfi.append_column(tvc)
        tvc=TextTVColumnEditable("arabtex",0,self.model_sfallomorfi)
        self.tvSfAllomorfi.append_column(tvc)

        self.model_smatches=gtk.ListStore(str,str)
        self.col_smatches={ "match": 0, "righe": 1 }

        self.tvSMatches.set_model(self.model_smatches)
        tvc=TransTVColumn("arabo",self.col_smatches["match"],VARABO)
        self.tvSMatches.append_column(tvc)
        tvc=TransTVColumn("trascrizione",self.col_smatches["match"],VTRASCRIZIONE)
        self.tvSMatches.append_column(tvc)
        tvc=TextTVColumn("righe",self.col_smatches["righe"])
        self.tvSMatches.append_column(tvc)
        tvc=TextTVColumn("arabtex",self.col_smatches["match"])
        self.tvSMatches.append_column(tvc)

        self.model_documento=gtk.ListStore(str,str,str)
        self.col_documento={ "tipo": 0, "match": 1, "righe": 2 }

        self.tvDocumento.set_model(self.model_documento)
        tvc=TextTVColumn("tipo",self.col_documento["tipo"])
        self.tvDocumento.append_column(tvc)
        tvc=TransTVColumn("arabo",self.col_documento["match"],VARABO)
        self.tvDocumento.append_column(tvc)
        tvc=TransTVColumn("trascrizione",self.col_documento["match"],VTRASCRIZIONE)
        self.tvDocumento.append_column(tvc)
        tvc=TextTVColumn("righe",self.col_documento["righe"])
        self.tvDocumento.append_column(tvc)
        tvc=TextTVColumn("arabtex",self.col_documento["match"])
        self.tvDocumento.append_column(tvc)

        self.model_subvoci=gtk.ListStore(str,str,str,str,str)
        self.tvSubvoci.set_model(self.model_subvoci)

        self.col_subvoci={ "voce": 0, "pronuncia": 1,
                           "categoria": 2,
                           "origine": 3,
                           "significato": 4 }

        tvc=TransTVColumn("arabo",self.col_subvoci["voce"],VARABO)
        self.tvSubvoci.append_column(tvc)
        tvc=TransTVColumn("trascrizione",self.col_subvoci["voce"],VTRASCRIZIONE)
        self.tvSubvoci.append_column(tvc)
        tvc=TextTVColumn("pronuncia",self.col_subvoci["pronuncia"])
        self.tvSubvoci.append_column(tvc)
        #tvc=TextTVColumn("cat.",self.col_subvoci["categoria"])
        #self.tvSubvoci.append_column(tvc)
        #tvc=TextTVColumn("or.",self.col_subvoci["origine"])
        #self.tvSubvoci.append_column(tvc)
        tvc=TextTVColumn("sign.",self.col_subvoci["significato"])
        self.tvSubvoci.append_column(tvc)
        tvc=TextTVColumn("arabtex",self.col_subvoci["voce"])
        self.tvSubvoci.append_column(tvc)

        self.model_contesti=gtk.ListStore(str,str,str)
        self.tvContesti.set_model(self.model_contesti)
        self.col_contesti={ "T": 0, "min": 1,
                            "max": 2 }
        tvc=TextTVColumn("min",self.col_contesti["min"])
        self.tvContesti.append_column(tvc)
        tvc=TextTVColumn("max",self.col_contesti["max"])
        self.tvContesti.append_column(tvc)
        tvc=TransTVColumn("arabo",self.col_contesti["T"],VARABO)
        self.tvContesti.append_column(tvc)
        tvc=TransTVColumn("trascrizione",self.col_contesti["T"],VTRASCRIZIONE)
        self.tvContesti.append_column(tvc)
        tvc=TextTVColumn("arabtex",self.col_contesti["T"])
        self.tvContesti.append_column(tvc)

        self.model_varianti=gtk.ListStore(str,str,str)
        self.tvVarianti.set_model(self.model_varianti)

        self.col_varianti={ "voce": 0, "pronuncia": 1,
                            "occasione": 2 }

        tvc=TransTVColumn("arabo",self.col_varianti["voce"],VARABO)
        self.tvVarianti.append_column(tvc)
        tvc=TransTVColumn("trascrizione",self.col_varianti["voce"],VTRASCRIZIONE)
        self.tvVarianti.append_column(tvc)
        tvc=TextTVColumn("pronuncia",self.col_varianti["pronuncia"])
        self.tvVarianti.append_column(tvc)
        tvc=TextTVColumn("occasione",self.col_varianti["occasione"])
        self.tvVarianti.append_column(tvc)
        tvc=TextTVColumn("arabtex",self.col_varianti["voce"])
        self.tvVarianti.append_column(tvc)

    # QUI
    def append_subvoce(self,s,parent,label,tipo,kfiltro="tvIndex"):
        (color,bullet)=decidi_colore(s,subvoce=True)
        color=color.replace("color","")
        if color and color!="sologlossario":
            csub="#%2.2x%2.2x%2.2x" % tuple(map(lambda x: x*255,VCOLORI[color]))
        else:
            csub="white"
        self.model_index.append(parent,[label,csub,s.voce,s,tipo,kfiltro])

    # QUI
    def append_voce(self,voce,parent,kfiltro="tvIndex"):
        (color,bullet)=decidi_colore(voce)
        color=color.replace("color","")
        if color:
            cstring="#%2.2x%2.2x%2.2x" % tuple(map(lambda x: x*255,VCOLORI[color]))
        else:
            cstring="white"

        cat=""
        if color=="solodoc":
            if type(voce)==ParSuffisso: cat="parsuffisso"
            else: cat="parola"
        else:
            if type(voce)==ParSuffisso: cat="parsuffisso"
            elif type(voce)==Suffisso: cat="suffisso"
            elif type(voce)==Parola: cat="parola"
            else: cat="voce"
            
        if color=="solodoc":
            vitem=self.model_index.append(parent,["D",cstring,voce.word,voce,
                                                  cat,kfiltro])
        elif color=="sologlossario":
            vitem=self.model_index.append(parent,["G",cstring,voce.voce,voce,cat,
                                                  kfiltro])
        elif color:
                vitem=self.model_index.append(parent,[color,cstring,voce.voce,voce,
                                                      cat,kfiltro])
        else:
            vitem=self.model_index.append(parent,["","white",voce.voce,voce,
                                                  cat,kfiltro])
        if cat!="voce": return(vitem)
        if voce.subvoci:
            for s in voce.subvoci:
                self.append_subvoce(s,vitem,"SUB","subvoce",kfiltro=kfiltro)
        if voce.varianti:
            for s in voce.varianti:
                self.append_subvoce(s,vitem,"VAR","variante",kfiltro=kfiltro)
        return(vitem)

    def cb_model_index_filter(self,model,iter,label):
        val=model.get_value(iter,5)
        return((label==val))
    
    def set_index(self):
        self.model_index=gtk.TreeStore(str,str,str,object,str,str)

        col_id={ "status": 0, "color": 1, "voce": 2 }

        self.model_index_f={}
        for k in self.tvindexkeys:
            self.model_index_f[k]=self.model_index.filter_new()
            self.model_index_f[k].set_visible_func(self.cb_model_index_filter,k)
            self.tvIndex[k].set_model(self.model_index_f[k])
            tvc=TextTVColumn("s.",col_id["status"],col_id["color"])
            self.tvIndex[k].append_column(tvc)
            tvc=TransTVColumn("arabo",col_id["voce"],VARABO,col_id["color"])
            self.tvIndex[k].append_column(tvc)
            tvc=TransTVColumn("trascrizione",col_id["voce"],VTRASCRIZIONE,col_id["color"])
            self.tvIndex[k].append_column(tvc)
            tvc=TextTVColumn("arabtex",col_id["voce"],col_id["color"])
            self.tvIndex[k].append_column(tvc)

        self.model_index.append(None,["Alfabeto","white","",None,"alfabeto",
                                      "tvIndexTabelle"])
        self.model_index.append(None,["Statistiche","white","",None,"statistiche",
                                      "tvIndexTabelle"])

        for cat in self.glossario.categorizzatori:
            if cat:
                print "OK",cat.title
                self.model_index.append(None,[cat.title,"white","",cat,
                                              "categoria","tvIndexCategorie"])
            else:
                print "NO",cat.title

        vgkeys=self.glossario.vottgrammaticali.keys()
        vgkeys.sort()

        for k in vgkeys:
            parent=self.model_index.append(None,[GRAMMATICALI[k],"white","",None,
                                                 "-","tvIndexGrammaticali"])
            for voce in self.glossario.vottgrammaticali[k]:
                self.append_voce(voce,parent,kfiltro="tvIndexGrammaticali")

        #for s in self.glossario.suffissi.get_all():
        #    self.append_voce(s,None,kfiltro="tvIndexSuffissi")

        tutti=self.glossario.solo_doc+self.glossario.vociottomane
        tutti.sort()

        elenco_items={}
        for voce in tutti:
            primo=voce.get_primo_carattere()
            if primo in HARAKAT_TUTTE:
                primo="A"
            elif primo in MULTIPLE.keys():
                primo=MULTIPLE[primo][0]
            elif primo in MULTIPLE_INIZIO.keys():
                primo=MULTIPLE_INIZIO[primo][0]

            if primo!="-":
                lett_ind=0
                while primo not in LETTERE[lett_ind]:
                    lett_ind+=1
                primo=LETTERE[lett_ind][0]
            if not elenco_items.has_key(primo):
                parent=self.model_index.append(None,["","white",primo,None,"-","tvIndex"])
                elenco_items[primo]=parent
            else:
                parent=elenco_items[primo]
            self.append_voce(voce,parent,kfiltro="tvIndex")

    def set_statistiche(self):
        model=gtk.ListStore(str,object)
        self.tvStatistiche.set_model(model)

        tvc=TextTVColumn("-",self.glossario.statistiche.col_keys["header"])
        self.tvStatistiche.append_column(tvc)
        #tvc=TotTVColumn("totale",range(1,self.glossario.statistiche.num_cols))
        tvc=TotTVColumn("totale")
        self.tvStatistiche.append_column(tvc)
        tvc=PercTVColumn("n.s.",self.glossario.statistiche.col_keys["n.s."]-1)
        self.tvStatistiche.append_column(tvc)

        for (o,ind) in self.glossario.statistiche.col_keys.items():
            if o=="header": continue
            if o=="n.s.": continue
            tvc=PercTVColumn(ORIGINI[o.upper()],ind-1)
            self.tvStatistiche.append_column(tvc)

        map(lambda x: model.append([x[0],x[1:]]),self.glossario.statistiche.R)
        
    def set_alfabeto(self):
        model_alfabeto=gtk.ListStore(str,str,str)
        self.tvAlfabeto.set_model(model_alfabeto)
        tvc=TextTVColumn("arabtex",0,2)
        self.tvAlfabeto.append_column(tvc)
        tvc=TransTVColumn("arabo",0,0,2)
        self.tvAlfabeto.append_column(tvc)
        tvc=TransTVColumn("triade",1,0,2)
        self.tvAlfabeto.append_column(tvc)
        tvc=TransTVColumn("trascrizione",0,1,2)
        self.tvAlfabeto.append_column(tvc)

        model_alfabeto.append(["'","'","white"])
        
        harakat=filter(lambda x: x not in [ "^a","^i","^r","^o", "N" ],HARAKAT_TUTTE)
        prime=ARAB_NORMAL+harakat
        altre=filter(lambda x: x not in prime+[ "^a","^i","^r","^o","N","'" ]+IGNORA,
                     ARAB_CONVERSIONE.keys())
        altre.sort(utility.alpha_compare)
        map(lambda x: model_alfabeto.append([x,x+"a"+x+"a"+x+"a","white"]),ARAB_NORMAL)
        map(lambda x: model_alfabeto.append([x,"","white"]),harakat)
        map(lambda x: model_alfabeto.append([x,x+"a"+x+"a"+x+"a","white"]),altre)
        map(lambda x: model_alfabeto.append([x,"b"+x,"white"]),[ "^a","^i","^r","^o" ])

    def load_categoria(self,catobj,catiter):
        self.model_categorie.clear()
        L=catobj.get_list()
        map(lambda x: self.model_categorie.append([x.voce,x,
                                                   "/".join(x.categorie),
                                                   x.origine]),L)
        if not catiter: return
        map(lambda x: self.append_voce(x,catiter,kfiltro="tvIndexCategorie"),L)

    def cb_tvindex_row_activated(self,tv,path,column):
        fmodel=tv.get_model()
	fiter=fmodel.get_iter(path)
        miter=fmodel.convert_iter_to_child_iter(fiter)
	iterobj=self.model_index.get_value(miter,3)
        itertype=self.model_index.get_value(miter,4)
        print itertype
        if itertype in [ "-" ]: return
        self.nbMain.set_current_page(self.pagine[itertype])
        if itertype in [ "categoria" ]:
            if self.model_index.iter_has_child(miter):
                catiter=None
            else:
                catiter=miter
            self.current=None
            self.current_iter=None
            self.current_subiter=None
            self.load_categoria(iterobj,catiter)
            return
        if itertype in [ "alfabeto", "statistiche" ]: 
            self.current=None
            self.current_iter=None
            self.current_subiter=None
            return
        if itertype=="voce":
            self.current_iter=miter
            self.current_subiter=None
        else:
            self.current_subiter=miter
            self.current_iter=None
        if itertype=="parola":
            self.load_parola(iterobj)
        elif itertype=="parsuffisso":
            self.load_parsuffisso(iterobj)
        elif itertype=="suffisso":
            self.load_suffisso(iterobj)
        elif itertype=="variante":
            self.load_variante(iterobj)
        else:
            self.load_voce(iterobj,itertype)

    def cb_buttondelsub_clicked(self,obj):
        parent=self.model_index.iter_parent(self.current_subiter)
        pobj=self.model_index.get_value(parent,3)
        pobj.subvoci.remove(self.current)
        self.model_index.remove(self.current_subiter)
        self.current_subiter=None
        self.load_voce(pobj,"voce")

    def cb_buttonsfdelete_clicked(self,obj): pass


    def cb_buttondelvoce_clicked(self,obj):
        next=self.model_index.iter_next(self.current_iter)
        if not next:
            parent=self.model_index.iter_parent(self.current_iter)
            npar=self.model_index.iter_next(parent)
            if npar:
                next=self.model_index.iter_children(npar)
        grammflag=False
        for c in self.current.categorie:
            if self.glossario.vottgrammaticali.has_key(c):
                grammflag=True
                self.glossario.vottgrammaticali[c].remove(self.current)
        if not grammflag:
            self.glossario.vociottomane.remove(self.current)
        self.model_index.remove(self.current_iter)
        self.current_subiter=None
        self.current_iter=next
        if next:
            obj=self.model_index.get_value(next,3)
            self.load_voce(obj,"voce")

    #QUI
    def load_variante(self,voceobj):
        self.current=voceobj
        self.entryVVoce.set_text(voceobj.voce)
        (color,bullet)=decidi_colore(self.current,subvoce=True)
        color=color.replace("color","")
        if color=="sologlossario":
            color=""
        if color:
            (red,green,blue)=map(lambda x: int(65535*x),VCOLORI[color])
        else:
            red=green=blue=65535
        self.eventVStatus.modify_bg(gtk.STATE_NORMAL,gtk.gdk.Color(red,green,blue))
        self.labelVStatus.set_label(color)

        self.labelVArabo.set_label(get_conversione(voceobj.voce,VARABO))
        self.labelVTrascrizione.set_label(get_conversione(voceobj.voce,VTRASCRIZIONE))
        if voceobj.pronuncia:
            self.entryVPronuncia.set_text(voceobj.pronuncia)
        else:
            self.entryVPronuncia.set_text("")
        if voceobj.occasione:
            self.entryVOccasione.set_text(voceobj.occasione)
        else:
            self.entryVOccasione.set_text("")
        buf=self.textviewVReference.get_buffer()
        if voceobj.references:
            slista=[]
            for (k,L) in voceobj.references.items():
                map(lambda x: slista.append(k+"/"+"/".join(x)),L)
            txt="\n".join(slista)
            buf.set_text(txt)
        else:
            buf.set_text("")
        buf=self.textviewVRefPronuncia.get_buffer()
        if voceobj.references_pron:
            slista=[]
            for (k,L) in voceobj.references_pron.items():
                map(lambda x: slista.append(k+"/"+"/".join(x)),L)
            txt="\n".join(slista)
            buf.set_text(txt)
        else:
            buf.set_text("")

    def load_parola(self,voceobj):
        self.current=voceobj
        self.entryPVoce.set_text(voceobj.word)
        color="solodoc"
        (red,green,blue)=map(lambda x: int(65535*x),VCOLORI[color])
        self.eventPStatus.modify_bg(gtk.STATE_NORMAL,gtk.gdk.Color(red,green,blue))
        self.labelPStatus.set_label(color)
        self.labelPArabo.set_label(get_conversione(voceobj.word,VARABO))
        self.labelPTrascrizione.set_label(get_conversione(voceobj.word,VTRASCRIZIONE))

    def load_parsuffisso(self,voceobj):
        self.current=voceobj
        self.entrySVoce.set_text(voceobj.word)
        color="solodoc"
        (red,green,blue)=map(lambda x: int(65535*x),VCOLORI[color])
        self.eventSStatus.modify_bg(gtk.STATE_NORMAL,gtk.gdk.Color(red,green,blue))
        self.labelSStatus.set_label(color)
        self.labelSArabo.set_label(get_conversione(voceobj.word,VARABO))
        self.labelSTrascrizione.set_label(get_conversione(voceobj.word,VTRASCRIZIONE))
        self.model_smatches.clear()
        for par in voceobj.parole:
            self.model_smatches.append( [par.word,par.righe_to_str()] )

    def cb_entryvoce_changed(self,obj):
        e=self.entryVoce.get_text()
        self.labelArabo.set_label(get_conversione(e,VARABO))
        self.labelTrascrizione.set_label(get_conversione(e,VTRASCRIZIONE))

    def cb_entryvvoce_changed(self,obj):
        e=self.entryVVoce.get_text()
        self.labelVArabo.set_label(get_conversione(e,VARABO))
        self.labelVTrascrizione.set_label(get_conversione(e,VTRASCRIZIONE))

    def cb_entrypvoce_changed(self,obj):
        e=self.entryPVoce.get_text()
        self.labelPArabo.set_label(get_conversione(e,VARABO))
        self.labelPTrascrizione.set_label(get_conversione(e,VTRASCRIZIONE))

    def cb_entrysvoce_changed(self,obj):
        e=self.entrySVoce.get_text()
        self.labelSArabo.set_label(get_conversione(e,VARABO))
        self.labelSTrascrizione.set_label(get_conversione(e,VTRASCRIZIONE))

    def cb_entrysfvoce_changed(self,obj):
        e=self.entrySfVoce.get_text()
        self.labelSfArabo.set_label(get_conversione(e,VARABO))
        self.labelSfTrascrizione.set_label(get_conversione(e,VTRASCRIZIONE))

    def load_voce(self,voceobj,tipo):
        self.current=voceobj
        self.entryVoce.set_text(voceobj.voce)
        self.checkVerificare.set_active(voceobj.verificare)
        if tipo=="voce":
            (color,bullet)=decidi_colore(self.current)
        else:
            (color,bullet)=decidi_colore(self.current,subvoce=True)
        color=color.replace("color","")
        if tipo!="voce" and color=="sologlossario":
            color=""
        if color:
            (red,green,blue)=map(lambda x: int(65535*x),VCOLORI[color])
        else:
            red=green=blue=65535
        self.eventStatus.modify_bg(gtk.STATE_NORMAL,gtk.gdk.Color(red,green,blue))
        self.labelStatus.set_label(color)
        self.labelIndice.set_label("("+str(voceobj.indice)+")")
        self.labelArabo.set_label(get_conversione(voceobj.voce,VARABO))
        self.labelTrascrizione.set_label(get_conversione(voceobj.voce,VTRASCRIZIONE))
        if voceobj.cosa_guardare:
            self.entryGuardare.set_text(voceobj.cosa_guardare)
        else:
            self.entryGuardare.set_text("")
        if voceobj.pronuncia:
            self.entryPronuncia.set_text(voceobj.pronuncia)
        else:
            self.entryPronuncia.set_text("")
        if voceobj.categorie:
            self.entryCategoria.set_text(":".join(voceobj.categorie))
        else:
            self.entryCategoria.set_text("")            
        if voceobj.origine:
            self.entryOrigine.set_text(voceobj.origine)
        else:
            self.entryOrigine.set_text("")            
        buf=self.textviewSignificato.get_buffer()
        if voceobj.significato:
            buf.set_text(voceobj.significato)
        else:
            buf.set_text("")

        buf=self.textviewNote.get_buffer()
        if voceobj.verificare and voceobj.noteverificare:
            buf.set_text(voceobj.noteverificare)
        else:
            buf.set_text("")
        
        buf=self.textviewReference.get_buffer()
        if voceobj.references:
            slista=[]
            for (k,L) in voceobj.references.items():
                map(lambda x: slista.append(k+"/"+"/".join(x)),L)
            txt="\n".join(slista)
            buf.set_text(txt)
        else:
            buf.set_text("")
        buf=self.textviewRefPronuncia.get_buffer()
        if voceobj.references_pron:
            slista=[]
            for (k,L) in voceobj.references_pron.items():
                map(lambda x: slista.append(k+"/"+"/".join(x)),L)
            txt="\n".join(slista)
            buf.set_text(txt)
        else:
            buf.set_text("")

        self.model_documento.clear()
        self.model_subvoci.clear()
        self.model_contesti.clear()
        self.model_varianti.clear()

        if tipo!="voce":
            self.frameAggiunte.set_property("visible",False)
            self.buttonAddSub.set_property("visible",False)
            self.buttonAddComposto.set_property("visible",False)
            self.buttonAddCompPrep.set_property("visible",False)
            self.buttonDelSub.set_property("visible",True)
            self.buttonDelVoce.set_property("visible",False)
            return
        
        self.frameAggiunte.set_property("visible",True)
        self.buttonAddSub.set_property("visible",True)
        self.buttonAddComposto.set_property("visible",True)
        self.buttonAddCompPrep.set_property("visible",True)
        self.buttonDelSub.set_property("visible",False)
        self.buttonDelVoce.set_property("visible",True)
        
        if voceobj.matches:
            for (sim,par) in voceobj.matches:
                self.model_documento.append( ["("+str(sim)+")",par.word,
                                              par.righe_to_str()] )
        if voceobj.subvoci:
            for s in voceobj.subvoci:
                self.model_subvoci.append([s.voce,s.pronuncia,":".join(s.categorie),
                                           s.origine,s.significato])
        if voceobj.varianti:
            for s in voceobj.varianti:
                self.model_varianti.append([s.voce,s.pronuncia,s.occasione])

        if voceobj.cosa_guardare:
            def f(x):
                a=str(x[0])+","+str(x[1])
                b=str(x[2])+","+str(x[3])
                return([x[4],a,b])
            map(lambda x: self.model_contesti.append(f(x)),
                self.glossario.get_contesti(voceobj))

    def load_suffisso(self,voceobj):
        self.current=voceobj
        self.entrySfVoce.set_text(voceobj.voce)
        self.checkSfVerificare.set_active(voceobj.verificare)
        red=green=blue=65535
        self.eventSfStatus.modify_bg(gtk.STATE_NORMAL,gtk.gdk.Color(red,green,blue))
        self.labelSfStatus.set_label("")
        self.labelSfArabo.set_label(get_conversione(voceobj.voce,VARABO))
        self.labelSfTrascrizione.set_label(get_conversione(voceobj.voce,VTRASCRIZIONE))

        if voceobj.input:
            self.entrySfInput.set_text(voceobj.input)
        else:
            self.entrySfInput.set_text("")
        if voceobj.categoria:
            self.entrySfCategoria.set_text(voceobj.categoria)
        else:
            self.entrySfCategoria.set_text("")
        if voceobj.output:
            self.entrySfOutput.set_text(voceobj.output)
        else:
            self.entrySfOutput.set_text("")

        if voceobj.classe:
            self.entrySfClasse.set_text(voceobj.classe)
        else:
            self.entrySfClasse.set_text("")            

        if voceobj.pronuncia:
            self.entrySfPronuncia.set_text(voceobj.pronuncia)
        else:
            self.entrySfPronuncia.set_text("")

        if voceobj.origine:
            self.entrySfOrigine.set_text(voceobj.origine)
        else:
            self.entrySfOrigine.set_text("")            
        buf=self.textviewSfSignificato.get_buffer()
        if voceobj.significato:
            buf.set_text(voceobj.significato)
        else:
            buf.set_text("")

        buf=self.textviewSfNote.get_buffer()
        if voceobj.verificare and voceobj.noteverificare:
            buf.set_text(voceobj.noteverificare)
        else:
            buf.set_text("")
        
        buf=self.textviewSfReference.get_buffer()
        if voceobj.references:
            slista=[]
            for (k,L) in voceobj.references.items():
                map(lambda x: slista.append(k+"/"+"/".join(x)),L)
            txt="\n".join(slista)
            buf.set_text(txt)
        else:
            buf.set_text("")
        buf=self.textviewSfRefPronuncia.get_buffer()
        if voceobj.references_pron:
            slista=[]
            for (k,L) in voceobj.references_pron.items():
                map(lambda x: slista.append(k+"/"+"/".join(x)),L)
            txt="\n".join(slista)
            buf.set_text(txt)
        else:
            buf.set_text("")

        self.model_sfparole.clear()
        if voceobj.matches:
            for (m,parsuffisso) in voceobj.matches:
                for par in parsuffisso.parole:
                    self.model_sfparole.append( [par.word,par.righe_to_str()] )

        self.model_sfallomorfi.clear()
        print voceobj.allomorfi
        if voceobj.allomorfi:
            map(lambda x: self.model_sfallomorfi.append([x]),
                voceobj.allomorfi)

    def cb_buttonpinglossario_clicked(self,obj):
        voce=self.entryPVoce.get_text()
        pron=self.entryPPronuncia.get_text()
        data="\\voceottomana{}{}{"+voce+"}{}{"+pron+"}{}{}"
        v=VoceOttomana(data)
        viter=self.append_voce(v,None,kfiltro="tvIndexNuove")
        self.glossario.vociottomane.append(v)
        self.current_iter=viter
        self.current_subiter=None
        self.current=v
        self.load_voce(v,"voce")

    def cb_buttonsinglossario_clicked(self,obj):
        voce=self.entrySVoce.get_text()
        pron=self.entrySPronuncia.get_text()
        data="\\suffisso{}{}{}{"+voce+"}{}{}{"+pron+"}{}{}{}{}"
        v=Suffisso(data)
        viter=self.append_voce(v,None,kfiltro="tvIndexNuove")
        self.glossario.suffissi.append(v)
        self.current_iter=viter
        self.current_subiter=None
        self.current=v
        self.load_suffisso(v)

    def cb_buttonaddcomposto_clicked(self,obj):
        self.action_addsub(composto="verbo")

    def cb_buttonaddcompprep_clicked(self,obj):
        self.action_addsub(composto="postposizione")

    def cb_buttonaddsub_clicked(self,obj):
        self.action_addsub()

    def action_addsub(self,composto=""):
        def evoce_changed(obj):
            e=eVoce.get_text()
            lA.set_label(get_conversione(e,VARABO))
            lT.set_label(get_conversione(e,VTRASCRIZIONE))
        def ctipo_changed(obj):
            ind=cTipo.get_active()
            vtipo=model[ind][0]
            ptipo=model[ind][1]
            eVoce.set_text(vtipo)
            ePron.set_text(ptipo)
        dic={}
        dic["on_entryVoce_changed"]=evoce_changed
        if composto:
            dic["on_comboTipo_changed"]=ctipo_changed
        wdxml=gtk.glade.XML(GLADES["addsub"])
        wdxml.signal_autoconnect(dic)
	wd=wdxml.get_widget("dialogMain")
        eVoce=wdxml.get_widget("entryVoce")
        cTipo=wdxml.get_widget("comboTipo")
        ePron=wdxml.get_widget("entryPronuncia")
        lA=wdxml.get_widget("labelArabo")
        lT=wdxml.get_widget("labelTrascrizione")
        if composto:
            model=gtk.ListStore(str,str)
            vbase=self.current.voce
            pbase=self.current.pronuncia
            if composto=="verbo":
                L=[ (" :EtB"," ėt-"),(" .QlB"," ol-"),(" .QlunB"," olun-"),
                    (" :GlB"," al-"),(" :v.ErB"," vėr-"), (" dur"," dur"),
                    (" b.UlB", " bul-") ]
            else:
                L=[ (" .Jl.H"," ile") ]
            for (v,p) in L:
                model.append( [ vbase+v, pbase+p ] )
        else:
            model=gtk.ListStore(str)
            model.append(["subvoceottomana"])
            model.append(["vottvariante"])
        c=gtk.CellRendererText()
        cTipo.pack_start(c,True)
        cTipo.add_attribute(c,'text',0)
        cTipo.set_model(model)
        wd.show()
        res=wd.run()
        if not res:
            wd.hide()
            return
        ind=cTipo.get_active()
        tipo=model[ind][0]
        voce=eVoce.get_text()
        pron=ePron.get_text()
        wd.hide()
        kfiltro=self.model_index.get_value(self.current_iter,5)
        if (not composto) and (tipo=="vottvariante"):
            data="\\vottvariante{}{"+voce+"}{}{"+pron+"}{}"
            v=VOttVariante(data)
            self.current.varianti.append(v)
            self.append_subvoce(v,self.current_iter,"VARn","variante",kfiltro=kfiltro)
            self.current_iter=None
            self.current_subiter=v
            self.load_variante(v)
            return
        data="\\subvoceottomana{}{}{"+voce+"}{}{"+pron+"}{}{}"
        v=VoceOttomana(data,sub=True)
        self.current.subvoci.append(v)
        self.append_subvoce(v,self.current_iter,"SUBn","subvoce",kfiltro=kfiltro)
        self.current_iter=None
        self.current_subiter=v
        self.load_voce(v,"subvoce")
        return

    def cb_buttonsfapply_clicked(self,obj):
        self.current.voce=self.entrySfVoce.get_text()
        self.current.pronuncia=self.entrySfPronuncia.get_text()
        self.current.origine=self.entrySfOrigine.get_text()
        self.current.input=self.entrySfInput.get_text()
        self.current.categoria=self.entrySfCategoria.get_text()
        self.current.output=self.entrySfOutput.get_text()
        self.current.classe=self.entrySfClasse.get_text()

        self.current.allomorfi=map(lambda x: x[0],self.model_sfallomorfi)

        buf=self.textviewSfSignificato.get_buffer()
        txt=buf.get_text(buf.get_start_iter(),buf.get_end_iter())
        self.current.significato=txt

        if self.checkSfVerificare.get_active():
            buf=self.textviewSfNote.get_buffer()
            txt=buf.get_text(buf.get_start_iter(),buf.get_end_iter())
            self.current.verificare=True
            self.current.noteverificare=txt
            print "a",txt

        buf=self.textviewSfReference.get_buffer()
        txt=buf.get_text(buf.get_start_iter(),buf.get_end_iter())
        if txt.strip():
            slista=txt.split("\n")
            ref={}
            for s in slista:
                t=s.split("/")
                if not ref.has_key(t[0]): ref[t[0]]=[]
                ref[t[0]].append(t[1:])
            self.current.references=ref
        else:
            self.current.references={}

        buf=self.textviewSfRefPronuncia.get_buffer()
        txt=buf.get_text(buf.get_start_iter(),buf.get_end_iter())
        if txt.strip():
            slista=txt.split("\n")
            ref={}
            for s in slista:
                t=s.split("/")
                if not ref.has_key(t[0]): ref[t[0]]=[]
                ref[t[0]].append(t[1:])
            self.current.references_pron=ref
        else:
            self.current.references_pron={}
        self.save(None)
        
    def cb_buttonapply_clicked(self,obj):
        self.current.voce=self.entryVoce.get_text()
        self.current.cosa_guardare=self.entryGuardare.get_text()
        self.current.pronuncia=self.entryPronuncia.get_text()
        self.current.origine=self.entryOrigine.get_text()
        cat=self.entryCategoria.get_text()
        self.current.categorie=cat.split(":")
        buf=self.textviewSignificato.get_buffer()
        txt=buf.get_text(buf.get_start_iter(),buf.get_end_iter())
        self.current.significato=txt

        if self.checkVerificare.get_active():
            buf=self.textviewNote.get_buffer()
            txt=buf.get_text(buf.get_start_iter(),buf.get_end_iter())
            self.current.verificare=True
            self.current.noteverificare=txt
            print "a",txt

        buf=self.textviewReference.get_buffer()
        txt=buf.get_text(buf.get_start_iter(),buf.get_end_iter())
        if txt.strip():
            slista=txt.split("\n")
            ref={}
            for s in slista:
                t=s.split("/")
                if not ref.has_key(t[0]): ref[t[0]]=[]
                ref[t[0]].append(t[1:])
            self.current.references=ref
        else:
            self.current.references={}

        buf=self.textviewRefPronuncia.get_buffer()
        txt=buf.get_text(buf.get_start_iter(),buf.get_end_iter())
        if txt.strip():
            slista=txt.split("\n")
            ref={}
            for s in slista:
                t=s.split("/")
                if not ref.has_key(t[0]): ref[t[0]]=[]
                ref[t[0]].append(t[1:])
            self.current.references_pron=ref
        else:
            self.current.references_pron={}
        self.save(None)

        (color,bullet)=decidi_colore(self.current)
        color=color.replace("color","")
        if color:
            cstring="#%2.2x%2.2x%2.2x" % tuple(map(lambda x: x*255,
                                                   VCOLORI[color]))
        else:
            cstring="white"
        #self.current_iter
        self.model_index.set_value(self.current_iter,1,cstring)
        
    def cb_buttonvapply_clicked(self,obj):
        self.current.voce=self.entryVVoce.get_text()
        self.current.pronuncia=self.entryVPronuncia.get_text()
        self.current.occasione=self.entryVOccasione.get_text()

        buf=self.textviewVReference.get_buffer()
        txt=buf.get_text(buf.get_start_iter(),buf.get_end_iter())
        if txt.strip():
            slista=txt.split("\n")
            ref={}
            for s in slista:
                t=s.split("/")
                if not ref.has_key(t[0]): ref[t[0]]=[]
                ref[t[0]].append(t[1:])
            self.current.references=ref
        else:
            self.current.references={}

        buf=self.textviewVRefPronuncia.get_buffer()
        txt=buf.get_text(buf.get_start_iter(),buf.get_end_iter())
        if txt.strip():
            slista=txt.split("\n")
            ref={}
            for s in slista:
                t=s.split("/")
                if not ref.has_key(t[0]): ref[t[0]]=[]
                ref[t[0]].append(t[1:])
            self.current.references_pron=ref
        else:
            self.current.references_pron={}
        self.save(None)

    def action_buttonref(self,textview,entry,combo):
        buf=textview.get_buffer()
        txt=buf.get_text(buf.get_start_iter(),buf.get_end_iter())
        pag=entry.get_text()
        ind=combo.get_active()
        model=combo.get_model()
        ref=model[ind][0]
        paghas=model[ind][1]
        txt=txt.strip()
        if txt: txt+="\n"
        txt+=ref
        if paghas:
            txt+="/"+pag
        buf.set_text(txt)

    def cb_buttonreference_clicked(self,obj):
        self.action_buttonref(self.textviewReference,
                              self.entryReference,
                              self.comboReference)
        #buf=self.textviewReference.get_buffer()
        #txt=buf.get_text(buf.get_start_iter(),buf.get_end_iter())
        #pag=self.entryReference.get_text()
        #ind=self.comboReference.get_active()
        #model=self.comboReference.get_model()
        #ref=model[ind][0]
        #paghas=model[ind][1]
        #txt=txt.strip()
        #if txt: txt+="\n"
        #txt+=ref
        #if paghas:
        #    txt+="/"+pag
        #buf.set_text(txt)

    def cb_buttonvreference_clicked(self,obj):
        self.action_buttonref(self.textviewVReference,
                              self.entryVReference,
                              self.comboVReference)
        #buf=self.textviewVReference.get_buffer()
        #txt=buf.get_text(buf.get_start_iter(),buf.get_end_iter())
        #pag=self.entryVReference.get_text()
        #ind=self.comboVReference.get_active()
        #model=self.comboVReference.get_model()
        #ref=model[ind][0]
        #txt=txt.strip()
        #if txt: txt+="\n"
        #txt+=ref+"/"+pag
        #buf.set_text(txt)

    def cb_buttonrefpronuncia_clicked(self,obj):
        self.action_buttonref(self.textviewRefPronuncia,
                              self.entryRefPronuncia,
                              self.comboRefPronuncia)
        #buf=self.textviewRefPronuncia.get_buffer()
        #txt=buf.get_text(buf.get_start_iter(),buf.get_end_iter())
        #pag=self.entryRefPronuncia.get_text()
        #ind=self.comboRefPronuncia.get_active()
        #model=self.comboRefPronuncia.get_model()
        #ref=model[ind][0]
        #txt=txt.strip()
        #if txt: txt+="\n"
        #txt+=ref+"/"+pag
        #buf.set_text(txt)

    def cb_buttonsfaddallomorfo_clicked(self,tv):
        self.model_sfallomorfi.append([""])
    
    def cb_buttonsfremoveallomorfo_clicked(self,tv):
        treesel=tv.get_selection()
        treesel.set_mode(gtk.SELECTION_SINGLE)
        (model,iter)=treesel.get_selected()
        if not iter: return
        model.remove(iter)

    def menu_glossario_export(self,obj):
        fname=get_filename_by_dialog(title="Export")
        fd=open(fname,'w')
        print "Opening "+fname
        self.glossario.print_items(fd)
        fd.close()

    def menu_glossario_export_matrix(self,obj):
        fname=get_filename_by_dialog(title="Export Matrix")
        fd=open(fname,'w')
        print "Opening "+fname
        self.glossario.print_matrix(fd)
        fd.close()

    def menu_glossario_export_statistiche(self,obj):
        fname=get_filename_by_dialog(title="Export Statistiche")
        fd=open(fname,'w')
        print "Opening "+fname
        self.glossario.print_statistiche(fd,full=False)
        fd.close()
    
    def menu_glossario_tex_categorie(self,obj):
        L_cats=filter(bool,self.glossario.categorizzatori)
        categorie=map(lambda x: x.title,L_cats)
        (fname,catind)=get_filename_categoria(categorie)
        fd=open(fname,'w')
        print "Opening "+fname
        L_cats[catind].print_tex_mini(fd)
        fd.close()
        
