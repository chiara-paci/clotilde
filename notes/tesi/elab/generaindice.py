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

parser.add_option("-o", "--output", dest="foutput", 
		  help="output FILE (default: %default)",
 		  metavar="FILE")
parser.add_option("-i", "--input", dest="finput", 
		  help="input FILE (default: %default)",
 		  metavar="FILE")

FOUTPUT_DEFAULT="-"
FINPUT_DEFAULT="-"

parser.set_defaults(finput=FINPUT_DEFAULT,
                    foutput=FOUTPUT_DEFAULT)
(options, args) = parser.parse_args()

def get_fullpath(fname):
    if not fname: return("-")
    if fname=="-": return("-")
    filtro=re.compile("^/.*")
    if not filtro.match(fname):
	return(os.getcwd()+"/"+fname)
    return(fname)

foutput=get_fullpath(options.foutput)
finput=get_fullpath(options.finput)

if foutput and foutput!="-":
    fdout=open(foutput,'w')
    print "Opening "+foutput
else:
    fdout=sys.stdout

if finput  and finput!="-":
    fdin=open(finput,'r')
    print "Opening "+finput
else:
    fdin=sys.stdout

from Analisi import Indice

x=Indice(fdin,fdout)
x.run()

if foutput and foutput!="-":
    fdout.close()
if finput and finput!="-":
    fdin.close()

