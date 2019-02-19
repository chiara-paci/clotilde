#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os
import optparse
import re

#HOMEHOME="/home/chiara"
HOMEHOME="/newbooks/miei"
#HOMEHOME="/penna"

HOME=HOMEHOME+"/tesi/elab"
DATA=HOMEHOME+"/tesi/database"
ORIG=HOMEHOME+"/tesi/testo/documento-tesi"

sys.path.append(HOME)

usage = "usage: %prog [options]"
parser = optparse.OptionParser(usage=usage,version="0.1")
parser.add_option("-t", "--trascrizione", dest="trascrizione", 
		  help="input FILE (default: %default)",
 		  metavar="FILE")
parser.add_option("-g", "--glossario", dest="glossario", 
		  help="input FILE (default: %default)",
 		  metavar="FILE")
parser.add_option("-p", "--pronuncie", dest="pronuncie", 
		  help="suffissi FILE (default: %default)",
 		  metavar="FILE")
parser.add_option("-r", "--reference", dest="reference", 
		  help="reference (default: %default)",
 		  metavar="FILE")
parser.add_option("-A","--g2p-to-db", action="store_true",
                  dest="add_to_db",
                  help="add to database (default: %default)")
parser.add_option("-X","--db-to-g2p", action="store_true",
                  dest="get_from_db",
                  help="get from database (default: %default)")
parser.add_option("-G","--glossario-to-g2p", action="store_true",
                  dest="get_from_glossario",
                  help="from glossario to g2b (default: %default)")
parser.add_option("-M","--match-glossario", action="store_true",
                  dest="match_glossario",
                  help="match glossario (default: %default)")
parser.add_option("-i", "--input", dest="finput", 
		  help="input FILE (default: %default)",
 		  metavar="FILE")
parser.add_option("-o", "--output", dest="foutput", 
		  help="output FILE (default: %default)",
 		  metavar="FILE")

TRASCRIZIONE_DEFAULT=ORIG+"/trascrizione.tex"
GLOSSARIO_DEFAULT=DATA+"/newglossario.db"
PRONUNCIE_DEFAULT=DATA+"/pronuncie.db"
FINPUT_DEFAULT="-"
FOUTPUT_DEFAULT="-"
REFERENCE_DEFAULT="bib/stein2006"

parser.set_defaults(trascrizione=TRASCRIZIONE_DEFAULT,
                    glossario=GLOSSARIO_DEFAULT,
                    pronuncie=PRONUNCIE_DEFAULT,
                    foutput="-",
                    finput="-",
                    add_to_db=False,
                    get_from_db=False,
                    get_from_glossario=False,
                    match_glossario=False,
                    reference=REFERENCE_DEFAULT
                    )

(options, args) = parser.parse_args()

def get_fullpath(fname):
    if not fname: return("-")
    if fname=="-": return("-")
    filtro=re.compile("^/.*")
    if not filtro.match(fname):
	return(os.getcwd()+"/"+fname)
    return(fname)
    
trascrizione=get_fullpath(options.trascrizione)
glossario=get_fullpath(options.glossario)
pronuncie=get_fullpath(options.pronuncie)
foutput=get_fullpath(options.foutput)

from Analisi import Documento, Glossario, Pronuncie

p=Pronuncie(pronuncie,options.reference)
p.load()

if options.add_to_db:
    p.load_g2p(options.finput)
    p.sort()
    p.save()
    sys.exit()

if options.get_from_db:
    p.save_g2p(options.foutput)
    sys.exit()

g=Glossario(glossario)
g.load()

if options.match_glossario:
    p.match_glossario(g)
    sys.exit()
