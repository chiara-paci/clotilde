#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os
import optparse
import re
import shutil

HOMEHOME="/home/chiara"
#HOMEHOME="/newbooks/miei"
#HOMEHOME="/penna"

HOME=HOMEHOME+"/tesi/elab"
ORIG=HOMEHOME+"/tesi/testo/documento-tesi"
DATA=HOMEHOME+"/tesi/database"

sys.path.append(HOME)

usage = "usage: %prog [options]"
parser = optparse.OptionParser(usage=usage,version="0.1")
parser.add_option("-t", "--trascrizione", dest="trascrizione", 
		  help="input FILE (default: %default)",
 		  metavar="FILE")
parser.add_option("-g", "--glossario", dest="glossario", 
		  help="input FILE (default: %default)",
 		  metavar="FILE")
parser.add_option("-s", "--suffissi", dest="suffissi", 
		  help="suffissi FILE (default: %default)",
 		  metavar="FILE")
parser.add_option("-f", "--forme", dest="forme", 
		  help="forme FILE (default: %default)",
 		  metavar="FILE")
parser.add_option("-r", "--radici", dest="radici", 
		  help="radici FILE (default: %default)",
 		  metavar="FILE")
parser.add_option("-a", "--forme-arabe", dest="formearabe", 
		  help="forme arabe FILE (default: %default)",
 		  metavar="FILE")
parser.add_option("-o", "--output", dest="foutput", 
		  help="output FILE (default: %default)",
 		  metavar="FILE")
parser.add_option("-d", "--divisioni", dest="divisioni", 
		  help="divisioni FILE (default: %default)",
 		  metavar="FILE")
parser.add_option("-G","--analizza-glossario", action="store_true",
                  dest="analizza_glossario",
                  help="analizza glossario (default: %default)")

TRASCRIZIONE_DEFAULT=ORIG+"/trascrizione.tex"
GLOSSARIO_DEFAULT=DATA+"/newglossario.db"
SUFFISSI_DEFAULT=DATA+"/suffissi.db"
RADICI_DEFAULT=DATA+"/arabo-radici.db"
FORME_DEFAULT=DATA+"/arabo-forme.db"
DIVISIONI_DEFAULT=DATA+"/divisioni.db"
FORMEARABE_DEFAULT=DATA+"/formearabe.db"
FOUTPUT_DEFAULT="-"

parser.set_defaults(trascrizione=TRASCRIZIONE_DEFAULT,
                    glossario=GLOSSARIO_DEFAULT,
                    suffissi=SUFFISSI_DEFAULT,
                    radici=RADICI_DEFAULT,
                    forme=FORME_DEFAULT,
                    divisioni=DIVISIONI_DEFAULT,
                    formearabe=FORMEARABE_DEFAULT,
                    analizza_glossario=False,
                    foutput="-")

(options, args) = parser.parse_args()

def get_fullpath(fname):
    if not fname: return("-")
    if fname=="-": return("-")
    filtro=re.compile("^/.*")
    if not filtro.match(fname):
	return(os.getcwd()+"/"+fname)
    return(fname)

def mk_backup(fname):
    fdir=os.path.dirname(fname)
    fbase=os.path.basename(fname)
    dlist=os.listdir(fdir)
    n=1
    while fbase+"."+str(n) in dlist:
        n+=1
    shutil.copyfile(fname,fname+"."+str(n))
    
trascrizione=get_fullpath(options.trascrizione)
glossario=get_fullpath(options.glossario)
radici=get_fullpath(options.radici)
forme=get_fullpath(options.forme)
suffissi=get_fullpath(options.suffissi)
divisioni=get_fullpath(options.divisioni)
formearabe=get_fullpath(options.formearabe)
foutput=get_fullpath(options.foutput)

mk_backup(glossario)
mk_backup(formearabe)
mk_backup(forme)
mk_backup(radici)

import gtk
import gtk.glade
from Analisi import Documento, Glossario, Parola, VGlossario, VFormeArabe

for a in [ ("Glossario",glossario),
           ("Radici",radici),
           ("Forme",forme),
           ("Suffissi",suffissi),
           ("Divisioni",divisioni),
           ("Forme Arabe",formearabe),
           ("Trascrizione",trascrizione),
           ("Output",foutput) ]:
    print "%12.12s: %s" % a

if options.analizza_glossario:
    print "Documento..."
    d=Documento(trascrizione)
    d.load()
    d.parole()

    print "Glossario..."
    g=Glossario(glossario,suffissi,formearabe)
    g.load()

    print "Glossario: add parole..."
    g.add_parole(d.words["Turco"],len(d.righe),d.max_len)

#g.suffissi.load_predivisioni(divisioni)

print "Ok si va"
gui=VFormeArabe(formearabe,forme,radici)
gui.load()
if options.analizza_glossario:
    gui.add_glossario(g)

gui.show()
gtk.main()
