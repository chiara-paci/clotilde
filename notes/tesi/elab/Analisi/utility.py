from config import *

def loc_print_row(fd,ch,sep="\\\\\n"):
    lab=ch.replace("_","\\_").replace("^","\\^{}")
    txt="&".join([lab,"\\TRL{"+ch+"}"]+map(lambda x: "\\RLbox{"+x+"}",
                                           [ ch, "B"+ch, "B"+ch+"B", ch+"B"]))
    fd.write(txt+sep)

def alpha_compare(areal,breal):
    if ( (areal in MULTIPLE.keys())
         and (breal in MULTIPLE.keys()) ):
        acfr=filter(lambda x: x not in IGNORA,MULTIPLE[areal])
        bcfr=filter(lambda x: x not in IGNORA,MULTIPLE[breal])
        L=min(len(acfr),len(bcfr))
        for n in range(0,L):
            ret=cmp(acfr[n],bcfr[n])
            if ret: return(ret)
        return(cmp(len(acfr),len(bcfr)))
    amult=False
    bmult=False
    if areal in MULTIPLE.keys():
        a=MULTIPLE[areal][0]
        amult=True
        b=breal
    elif breal in MULTIPLE.keys():
        a=areal
        bmult=True
        b=MULTIPLE[breal][0]
    else:
        a=areal
        b=breal
    if a=="'" and b=="'":
        if amult: return(1)
        if bmult: return(-1)
        return(0)
    if a=="'": return(1)
    if b=="'": return(-1)
    if (a in HARAKAT_TUTTE) and (b in HARAKAT_TUTTE):
        ret=cmp(ORDER_HARAKAT[a],ORDER_HARAKAT[b])
        if ret: return(ret)
        if amult: return(1)
        if bmult: return(-1)
        return(0)
    if (a not in HARAKAT_TUTTE) and (b not in HARAKAT_TUTTE):
        ret=cmp(ORDER_LETTERE[a],ORDER_LETTERE[b])
        if ret: return(ret)
        if amult: return(1)
        if bmult: return(-1)
        return(0)
    if (a in HARAKAT_TUTTE): return(-1)
    return(1)

#fd.write("\\resizebox{\\textwidth}{!}{\\begin{tabular}{|*{2}{cccccc|}}\n")
def loc_print_alpha_tab(fd,titolo,label,elenco,vocalize=False):
    L=len(elenco)
    M=int(round((L+0.5)/3.0))
    fd.write("\\tabula{Arabtex. "+titolo+"}{tab:"+label+"}{")
    if vocalize:
        fd.write("\\vocalize\n")
    else:
        fd.write("\\novocalize\n")
    fd.write("\\begin{minipage}{\\textwidth}\n")
    fd.write("\\begin{center}\n")
    fd.write("\\begin{tabular}{|*{3}{cccccc|}}\n")
    fd.write("\\hline\n")
    for n in range(0,M):
        ch=elenco[n]
        loc_print_row(fd,ch,sep=" & ")
        ch=elenco[n+M]
        loc_print_row(fd,ch,sep=" & ")
        if n+2*M<L:
            ch=elenco[n+2*M]
            loc_print_row(fd,ch)
        else:
            fd.write("\\\\\n")
    fd.write("\\hline\n")
    fd.write("\\end{tabular}\n")
    fd.write("\\end{center}\n")
    fd.write("\\end{minipage}}\n")

def print_alphabet(fd):
    loc_print_alpha_tab(fd,"Consonanti","otarabtexconsonanti",ARAB_NORMAL)
    harakat=filter(lambda x: x not in [ "^a","^i","^r" ],HARAKAT_TUTTE)
    loc_print_alpha_tab(fd,"Vocali brevi","otarabtexbrevi",harakat,vocalize=True)
    fatte=ARAB_NORMAL+harakat
    altre=filter(lambda x: x not in fatte+[ "^a","^i","^r","B","N","-" ],
                 ARAB_CONVERSIONE.keys())
    altre.sort(cmp=alpha_compare)
    altre+=[ "b^a","b^r","b^i" ]
    loc_print_alpha_tab(fd,"Altre","otarabtexaltre",altre)
