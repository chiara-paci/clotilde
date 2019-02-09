#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os
import optparse
import re

HOMEHOME="/home/chiara"
#HOMEHOME="/newbooks/miei"
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
parser.add_option("-f", "--forme", dest="forme", 
		  help="forme FILE (default: %default)",
 		  metavar="FILE")
parser.add_option("-r", "--radici", dest="radici", 
		  help="radici FILE (default: %default)",
 		  metavar="FILE")
parser.add_option("-s", "--suffissi", dest="suffissi", 
		  help="suffissi FILE (default: %default)",
 		  metavar="FILE")
parser.add_option("-o", "--output", dest="foutput", 
		  help="output FILE (default: %default)",
 		  metavar="FILE")
parser.add_option("-G","--analizza-glossario", action="store_true",
                  dest="analizza_glossario",
                  help="analizza glossario (default: %default)")
parser.add_option("-Q","--estrai-suffissi", action="store_true",
                  dest="estrai_suffissi",
                  help="estrai suffissi (default: %default)")
parser.add_option("-T","--out-trascrizione", action="store_true",
                  dest="out_trascrizione",
                  help="trascrizione (default: %default)")
parser.add_option("-F","--analizza-forme-arabe", action="store_true",
                  dest="analizza_formearabe",
                  help="analizza forme arabe (default: %default)")
parser.add_option("-S","--salva-glossario", action="store_true",
                  dest="salva_glossario",
                  help="salva glossario (default: %default)")
parser.add_option("-X","--print-statistiche", action="store_true",
                  dest="print_statistiche",
                  help="print statistiche (default: %default)")
parser.add_option("-Y","--print-statistiche-rid", action="store_true",
                  dest="print_statistiche_rid",
                  help="print statistiche rid (default: %default)")
parser.add_option("-A","--alphabet",action="store_true",
                  dest="alphabet",
                  help="alphabet (default: %default)")
parser.add_option("-C","--confronto",action="store_true",
                  dest="confronto",
                  help="confronto (default: %default)")
parser.add_option("-a", "--forme-arabe", dest="formearabe", 
		  help="forme arabe FILE (default: %default)",
 		  metavar="FILE")

TRASCRIZIONE_DEFAULT=ORIG+"/trascrizione.tex"
GLOSSARIO_DEFAULT=DATA+"/newglossario.db"
SUFFISSI_DEFAULT=DATA+"/suffissi.db"
DIVISIONI_DEFAULT=DATA+"/divisioni.db"
FORMEARABE_DEFAULT=DATA+"/formearabe.db"
RADICI_DEFAULT=DATA+"/arabo-radici.db"
FORME_DEFAULT=DATA+"/arabo-forme.db"
FOUTPUT_DEFAULT="-"

parser.set_defaults(trascrizione=TRASCRIZIONE_DEFAULT,
                    glossario=GLOSSARIO_DEFAULT,
                    suffissi=SUFFISSI_DEFAULT,
                    formearabe=FORMEARABE_DEFAULT,
                    radici=RADICI_DEFAULT,
                    forme=FORME_DEFAULT,
                    out_trascrizione=False,
                    analizza_glossario=False,
                    estrai_suffissi=False,
                    analizza_formearabe=False,
                    salva_glossario=False,
                    print_statistiche=False,
                    print_statistiche_rid=False,
                    alphabet=False,
                    confronto=False,
                    foutput="-")

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
radici=get_fullpath(options.radici)
forme=get_fullpath(options.forme)
suffissi=get_fullpath(options.suffissi)
foutput=get_fullpath(options.foutput)
#divisioni=get_fullpath(options.divisioni)
formearabe=get_fullpath(options.formearabe)

if options.alphabet:
    from Analisi import utility
    if foutput and foutput!="-":
        fd=open(foutput,'w')
        print "Opening "+foutput
    else:
        fd=sys.stdout
    utility.print_alphabet(fd)
    if foutput and foutput!="-":
        fd.close()
    sys.exit()

if options.print_statistiche_rid:
    options.print_statistiche=True

from Analisi import Documento, Glossario, Parola, VFormeArabe

d=Documento(trascrizione)
d.load()
d.parole()

for a in [ ("Glossario",glossario),
           ("Suffissi",suffissi),
           ("Trascrizione",trascrizione),
           ("Output",foutput) ]:
    print "%12.12s: %s" % a

if options.out_trascrizione:
    if foutput and foutput!="-":
        fd=open(foutput,'w')
        print "Opening "+foutput
    else:
        fd=sys.stdout
    d.trascrizione(fd)
    if foutput and foutput!="-":
        fd.close()
    sys.exit()


#g=Glossario(glossario)
g=Glossario(glossario,suffissi,formearabe)
g.load()

if options.analizza_formearabe:
    fa=VFormeArabe(formearabe,forme,radici)
    fa.load()
    fa.add_glossario(g)
    if foutput and foutput!="-":
        fd=open(foutput,'w')
        print "Opening "+foutput
    else:
        fd=sys.stdout
    fa.print_tex(fd)
    if foutput and foutput!="-":
        fd.close()
    sys.exit()

if options.salva_glossario:
    if foutput and foutput!="-":
        fd=open(foutput,'w')
        print "Opening "+foutput
    else:
        fd=sys.stdout
    g.save(fd)
    if foutput and foutput!="-":
        fd.close()
    sys.exit()

g.add_parole(d.words["Turco"],len(d.righe),d.max_len)

if options.print_statistiche:
    if foutput and foutput!="-":
        fd=open(foutput,'w')
        print "Opening "+foutput
    else:
        fd=sys.stdout
    if options.print_statistiche_rid:
        g.print_statistiche(fd,full=False)
    else:
        g.print_statistiche(fd,full=True)
    if foutput and foutput!="-":
        fd.close()
    sys.exit()

if options.confronto:
    if foutput and foutput!="-":
        fd=open(foutput,'w')
        print "Opening "+foutput
    else:
        fd=sys.stdout
    g.print_cfr(fd,d)
    if foutput and foutput!="-":
        fd.close()
    sys.exit()

if options.analizza_glossario:
    if foutput and foutput!="-":
        fd=open(foutput,'w')
        print "Opening "+foutput
    else:
        fd=sys.stdout
    g.print_items(fd)
    #g.print_matrix(fd)
    if foutput and foutput!="-":
        fd.close()
    sys.exit()

if options.estrai_suffissi:
    if foutput and foutput!="-":
        fd=open(foutput,'w')
        print "Opening "+foutput
    else:
        fd=sys.stdout
    g.print_suffissi_calcolati(fd)
    #g.print_matrix(fd)
    if foutput and foutput!="-":
        fd.close()
    sys.exit()

