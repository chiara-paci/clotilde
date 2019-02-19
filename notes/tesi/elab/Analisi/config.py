# -*- coding: utf-8 -*-

HOMEHOME="/home/chiara"
#HOMEHOME="/newbooks/miei"

DRAFT=False

import sys
IGNORA=[ "|", "-", " ", "B", "?" ]

TURCHE_IN_ARABO=[ ":vened.Ik" , "d.O^z.I" ]

SWITCHES=[ "_","^",":","." ]

SEZIONI=[ "Turco", "Nomi Propri", "Arabo" ]

LETTERE=[ [ "A","^A","^E",":A","_E","^J","^j",":c",":C", ":G" ],
          [ "b" ],
          [ "p" ],
          [ "t" ],
          [ "_t" ],
          [ "^g" ],
          [ "^c" ],
          [ ".h" ],
          [ "_h" ],
          [ "d" ],
          [ "_d" ],
          [ "r" ],
          [ "z" ],
          [ "^z" ],
          [ "s" ],
          [ "^s" ],
          [ ".s" ],
          [ ".d" ],
          [ ".t" ],
          [ ".z" ],
          [ "`" ],
          [ ".g" ],
          [ "f" ],
          [ "q" ],
          [ "k", ":k" ],
          [ "g" ],
          [ "^n", "^N", "_n" ],
          [ "l" ],
          [ "m" ],
          [ "n" ],
          [ "w","U",":v",".O",":O",".U",":U","_w" ],
          [ "h","T","_T",":T",".T","_H",":H",".H","^H","H",":h" ],
          [ "y","I",".I",":I",".E","Y",".Y",":Y", "_Y" ] ]

LETTERE_RADICI_ARABE=[ "'", "b", "p", "t", "_t", "^g", "^c", ".h", "_h",
                       "d", "_d", "r", "z", "^z", "s", "^s", ".s", ".d",
                       ".t", ".z", "`", ".g", "f", "q", "k", "g", "^n",
                       "l", "m", "n", "w", "h", "y" ]

HARAKAT=[ [ "a", ":a", "^a", "^r", "aN" ],
          [ "e", ".e", ":i", "i", "^i", "^J" ],
          [ "o", ":o", "u", ":u", "uN" ] ]

NUN_SIGN="N"
IZAFET_SIGN="-"

HARAKAT_IND={ "a": 0, "i": 1, "u": 2 }

HAMZA=[ "'", "^o" ]


HARAKAT_TUTTE=reduce(lambda x,y: x+y,HARAKAT)
LETTERE_TUTTE=reduce(lambda x,y: x+y,LETTERE)

HARAKAT_SILENTI=filter(lambda x: x not in [ "^a", "^r", "^i" ], HARAKAT_TUTTE)

VOCALI_LUNGHE=LETTERE[0]+LETTERE[-1][1:]+LETTERE[-3][1:]

MULTIPLE={ ":E": ( "A", "y" ),
           ".J": ( "A", "y" ),
           ":J": ( "A", "y" ),
           ".Q": ( "A", "w" ),
           ":Q": ( "A", "w" ),
           ".W": ( "A", "w" ),
           ":W": ( "A", "w" ),
           "^h": ( "h","-","i" ),
           "^k": ( "h","-","i" )
           }

MULTIPLE_INIZIO = { "I": ( "A", "y" ),
                    "U": ( "A", "w" ) }

ORDER_LETTERE={}
ORDER_HARAKAT={ "sukun": 0 }

for n in range(0,len(HARAKAT)):
    for ch in HARAKAT[n]:
        ORDER_HARAKAT[ch]=n+1

for n in range(0,len(LETTERE)):
    for ch in LETTERE[n]:
        ORDER_LETTERE[ch]=n
    
class CharNotExists(Exception):
    def __init__(self,ch):
        self.ch=ch

    def __str__(self):
	return(self.ch+" non esiste")

ABBREVIAZIONI={ "A": "arabo",
                "P": "persiano",
                "T": "turco",
                "G": "greco",
                "M": "mediterraneo",
                "I": "italiano",
                "AT": "arabo-turco",
                "APT": "arabo-persiano-turco",
                "PT": "persiano-turco",
                "TA": "turco-arabo",
                "TP": "turco-persiano",
                "AP": "arabo-persiano",
                "L": "latino",
                "C": "cinese",
                "num": "numero",
                "n": "nome",
                "v": "verbo",
                "sc": "stato costrutto",
                "va": "verbo ausiliario",
                "np": "nome proprio",
                "loc": "locuzione",
                "agg": "aggettivo",
                "aggc": "agg. comparativo",
                "aggs": "agg. superlativo",
                "aggn": "agg. numerale",
                "aggp": "agg. pronominale",
                "avv": "avverbio",
                "cong": "congiunzione",
                "pron": "pronome",
                "post": "postposizione",
                "int": "interiezione" }

GRAMMATICALI={ "va": "Verbi ausiliari",
               "pron" : "Pronomi",
               "num" : "Numerali",
               "qta": "Quantificatori",
               "aggn": "Aggettivi numerali",
               "aggp": "Aggettivi pronominali",
               "np": "Nomi Propri",
               "post": "Post e preposizioni",
               "cong" : "Congiunzioni" }

NON_GRAMMATICALI={ "n": "Nomi",
                   "v": "Verbi",
                   "loc": "Locuzioni",
                   "agg": "Aggettivi",
                   "aggc": "Aggettivi comparativi",
                   "aggs": "Aggettivi superlativi",
                   "sc": "Stati costrutti",
                   "avv": "Avverbi",
                   "int": "Interiezioni" }

TUTTE_CATEGORIE=dict(GRAMMATICALI.items()+NON_GRAMMATICALI.items())

ORIGINI=dict(filter(lambda k: k[0] not in TUTTE_CATEGORIE.keys(),
                    ABBREVIAZIONI.items()))

ORIGINI_ARABE=[ "a", "at", "apt", "ap" ]

ORDINE_GRAMMATICALI=[ "np", "va", "pron", "aggp", "post", "cong",
                      "qta" ,"num", "aggn" ]

FONTI_PRONUNCIA={ "redhouse1997": ("cont",1.0),
                  "timurtas1999": ("cont",1.0),
                  "kiefferbianchi18351": ("cont",0.50)}

COLORA={ "nonorigine": True,
         "nonref": True,
         "nonrefpron": False,
         "lowref": True,
         "lowrefpron": False,
         "nosignificato": True }

COLORI_ORDINE=[ "lowref", "lowrefpron",
                "nosignificato", "nonorigine",
                "nonrefpron", "nonref" ]


COLORI={ "nonorigine": (0.8,0.4,0),
         "nonref": (1,0,1),
         "lowref": (0.5,0,0),
         "lowrefpron": (0.5,0,0),
         "nonrefpron": (1,0,1),
         "nosignificato": (1,0,0),
         "sologlossario": (0.5,0.5,0.5),
         "solodoc": (0,0.5,0) }

def list_to_unicode(seq):
    ret=u''
    for s in seq:
        ret+=u"%c" % s
    return(ret)

a_underscore=[0x61,0x0331]
ee_underscore=[0x117,0x0331]
e_underscore=[0x65,0x0331]
i_underscore=[0x69,0x0331]
o_underscore=[0x6f,0x0331]
u_underscore=[0x75,0x0331]
oe_underscore=[0xf6,0x0331]
uu_underscore=[0xfc,0x0331]
ii_underscore=[0x131,0x0331]

t_underscore=[0x74,0x331]
d_underscore=[0x64,0x331]
h_underscore=[0x68,0x331]
h_undercup=[0x1e2b]

ha_hamza_kasra=[0x0647,0x064e,0x654]

alif_madda=[0x0622]
ottoman_cin=[0x0686]
ottoman_jah=[0x0698]
ottoman_gaf=[0x06af]
ottoman_naf=[0x0763]
ottoman_naf_bis=[0x063b]
ottoman_naf_ter=[0x063c]
ottoman_kaf=[0x06a9]
ottoman_pa=[0x067e]
ya_without_dots=[0x0649]
ha_with_hamza=[0x6c0]
hamza=[0x621]

little_w=[0x31a]
madda_sign=[0x6e4]

fatha_n=[0x064b]
kasra=[0x0650]
little_alif=[0x670]

# "'"
ARAB_CONVERSIONE={
    "b": ( "ب", "b" ),
    "p": ( ottoman_pa, "p" ),
    "t": ( "ت", "t" ),
    "_t": ( "ث", t_underscore ),
    "^g": ( "ج", "ǧ" ),
    "^c": ( ottoman_cin, "č" ),
    ".h": ( "ح", "ḥ" ),
    "_h": ( "خ", h_undercup ),
    "d": ( "د", "d" ),
    "_d": ( "ذ", d_underscore ),
    "r": ( "ر", "r" ),
    "z": ( "ز", "z" ),
    "^z": ( ottoman_jah, "ž" ),
    "s": ( "س", "s" ),
    "^s": ( "ش", "š" ),
    ".s": ( "ص", "ṣ" ),
    ".d": ( "ض", "ḍ" ),
    ".t": ( "ط", "ṭ" ),
    ".z": ( "ظ", "ẓ" ),
    "`": ( "ع", "`" ),
    ".g": ( "غ", "ġ" ),
    "f": ( "ف", "f" ),
    "q": ( "ق", "q" ),
    "k": ( ottoman_kaf, "k" ),
    "g": ( ottoman_gaf, "g" ),
    "^n": ( ottoman_naf_bis, "ŋ" ),
    "l": ( "ل", "l" ),
    "m": ( "م", "m" ),
    "n": ( "ن", "n" ),
    "w": ( "و", "w" ),
    ":v": ( "و", "v" ),
    "h": ( "ه", "h" ),
    "y": ( "ي", "y" ),

    # harakat: solo trascrizione, compaiono come alif se sono iniziali
    ":i": ( "", "ı" ),
    "i":  ( "", "i" ),
    "^J":  ( "", "i" ),
    "o":  ( "", "o" ),
    ":o": ( "", "ö" ),

    "a":  ( "", "a" ),
    ":a": ( "", "e" ),
    "e":  ( "", "e" ),
    ".e": ( "", "ė" ),

    "u":  ( "", "u" ),
    ":u": ( "", "ü" ),

    # altro (queste compaiono sempre)

    ":c": ( "ا", "a" ),
    "_E": ( "ا", ee_underscore ),
    ":G": ( alif_madda, a_underscore ),
    ":A": ( "ا", "ā" ),
    ":C": ( alif_madda, "ā" ),
    "A":  ( "ا", "ā" ),
    "^A": ( "ا", a_underscore ),
    "^E": ( "ا", e_underscore ),
    ":W": ( "او", uu_underscore ),
    ":Q": ( "او", oe_underscore ),
    ".Q": ( "او", o_underscore ),
    ".W": ( "او", u_underscore ),
    ":J": ( "اي", ii_underscore ),
    ":E": ( "اي", ee_underscore ),
    ".J": ( "اي", i_underscore ),
    "_w": ( "و", little_w ),
    ":O": ( "و", oe_underscore ),
    ":U": ( "و", uu_underscore ),
    ".U": ( "و", u_underscore ),
    ".O": ( "و", o_underscore ),
    "U":  ( "و", "ū" ),
    "_H": ( "ه", "t" ),
    ":H": ( "ه", "ạ" ),
    ".H": ( "ه", "ẹ" ),
    "^H": ( "ه", "ị" ),
    "T":  ( "ة", "h" ),
    "_T": ( "ة", "t" ),
    ":T": ( "ة", "ạ" ),
    ".T": ( "ة", "ẹ" ),

    ".E": ( "ي", ee_underscore ),
    "I":  ( "ي", "ī" ),
    "Y":  ( ya_without_dots, "ā" ),
    ":Y": ( ya_without_dots, ii_underscore ),
    ":I": ( "ي", ii_underscore ),
    ".I": ( "ي", i_underscore ),
    ".Y": ( ya_without_dots, i_underscore ),
    "_Y": ( ya_without_dots, "ī" ),

    ":k": ( "ك", "k" ),
    "^N": ( ottoman_naf_ter, "ŋ" ),
    "_n": ( ottoman_naf, "ŋ" ),
    "^h": ( ha_hamza_kasra, "ẹ-i" ),
    "^k": ( ha_hamza_kasra, "ạ-i" ),
    ":h": ( ha_with_hamza, "ẹ-" ),

    # servizio
    "N":  ( "", "n" ),
    "-":  ( "", "-" ),
    "B":  ( "", "-" ),
    " ":  ( " "," "),

    "'": ( hamza, "'" ),
    "^a": ( fatha_n, "an" ),
    "^r": ( little_alif, a_underscore ),
    "^i": ( kasra, "i" ),
    "^o": ( hamza,"'")
    }

# se è  valorizzato e  il valore è  non nullo,  lo usa al  posto della
# tabella precedente

#                isolata, iniziale, mediana, finale

VARIANTI={ "U": ( "او", "او", "", "" ),
           "I": ( "اي", "اي", "", "" ),
           ":G": ( "", "", "ا", "ا" ),
           #":C": ( "", "", madda_sign, madda_sign ),
           #"^n": ( "", "", ottoman_naf_bis, "" )
           }

for ch in HARAKAT_SILENTI:
    VARIANTI[ch]=( "ا", "ا", "", "" )

ARAB_NORMAL=[ "b","p","t","_t","^g","^c",".h","_h","d","_d",
              "r","z","^z","s","^s",".s",".d",".t",".z","`",
              ".g","f","q","k","g","^n","l","m","n","w",":v","h","y" ]


def spzrl(S):
    if S[0]!="{":
        return("\\spzrl{"+S+"}")
    if S[-1]!="}":
        return("\\spzrl{"+S+"}")
    return("\\spzrl"+S)

def spzrltab(text):
    if text[0]=="{":
        return("\\spzrltab"+text)
    return("\\spzrltab{"+text+"}")

def reftotex(text,vuoto="\\manca{}"):
    def map_ref(B,tipo):
        T="\\"+tipo
        if len(B)>1: T+="["+B[1]+"]"
        T+="{"+B[0]+"}"
        return(T)

    fmap={ "bib": lambda x: map_ref(x,"spzcite"),
           "tab": lambda x: map_ref(x,"tabella"),
           "sec": lambda x: map_ref(x,"sezione") }

    if not text: return("")
    L=[]
    for pref in text.split(";"):
        r=pref.split("/")
        if len(r)<=1: continue
        k=r[0]
        D=r[1:]
        if k in ["tab","sec"]:
            L.append(fmap[k](D))
        else:
            if len(D)==1:
                D.append(vuoto)
            L.append(fmap[k](D))
    return(", ".join(L)+"\n")


IMGDIR=HOMEHOME+"/tesi/elab/Analisi/icone"
GLADEDIR=HOMEHOME+"/tesi/elab/Analisi/glade"
#GLADEDIR="/penna/tesi/elab/Analisi/glade"
GLADES={ "glossario": GLADEDIR+"/glossario.glade",
         "divisioni": GLADEDIR+"/divisioni.glade",
         "formearabe": GLADEDIR+"/formearabe.glade",
         "filesaver": GLADEDIR+"/filesaver.glade",
         "filesaver-categorie": GLADEDIR+"/filesaver-categorie.glade",
         "filechooser": GLADEDIR+"/filechooser.glade",
         "confirmation": GLADEDIR+"/confirmation.glade",
         "addsub": GLADEDIR+"/addsub.glade",
         }

REPORT_FOLDER="file:///"+HOMEHOME+"/tesi/testo/report"

TO_G2P_CONVERSIONI={}

for ch in [ "a","i","u", "A", "b", "p", "t", "'", "d", "r", "z", "s", "f", "`",
            "q", "k", "g", "l", "m", "n", "w", "U", "y","I", "h" ]:
    TO_G2P_CONVERSIONI[ch]=ch

TO_G2P_CONVERSIONI["_t"]="T"
TO_G2P_CONVERSIONI["^g"]="ǧ"
TO_G2P_CONVERSIONI["^c"]="č"
TO_G2P_CONVERSIONI[".h"]="ḥ"
TO_G2P_CONVERSIONI["_h"]="ḫ"
TO_G2P_CONVERSIONI["_d"]="D"
TO_G2P_CONVERSIONI["^z"]="ž"
TO_G2P_CONVERSIONI["^s"]="š"
TO_G2P_CONVERSIONI[".s"]="ṣ"
TO_G2P_CONVERSIONI[".d"]="ḍ"
TO_G2P_CONVERSIONI[".t"]="ṭ"
TO_G2P_CONVERSIONI[".z"]="ẓ"
TO_G2P_CONVERSIONI[".g"]="ġ"
TO_G2P_CONVERSIONI["^n"]="ŋ"
TO_G2P_CONVERSIONI["aT"]="H"
TO_G2P_CONVERSIONI["aN"]="E"
TO_G2P_CONVERSIONI["uN"]="W"
TO_G2P_CONVERSIONI["iN"]="J"

FROM_G2P_CONVERSIONI={}
for (k,ch) in TO_G2P_CONVERSIONI.items():
    FROM_G2P_CONVERSIONI[ch]=k

LINGUE={"": "non spec.",
        "es": "Spagnolo (Castigliano)",
        "cat": "Catalano",
        "biz":"Bizantino",
        "bal":"Area Balcanica",
        "ru":"Rumeno",
        "it": "Italiano",
        "ar": "Arabo",
        "ott": "Ottomano",
        "gr": "Greco",
        "per": "Persiano",
        "cin": "Cinese",
        "itve": "Veneziano",
        "latmed": "Latino medievale",
        "fr": "Francese",
        "en": "Inglese",
        "nl": "Olandese",
        "atr": "Radici turche",
        "lat": "Latino classico",
        "trt": "Turco di Turchia",
        "kar": "Karaim",
        "az": "Azeri",
        "tv": "Tuvino",
        "tkm": "Turkmeno",
        "uzb": "Uzbeco",
        "cag": "Ciagataico",
        "kip": "Kıpchak?",
        "xak": "Xak?",
        "xwar": "Xwar?",
        "khak": "Khak?",
        "kom": "Kom?",
        "trk": "Antico Turco",
        "yak": "Yakuto",
        "mong": "Mongolo",
        "hu": "Ungherese" }


LETTERE_RADICI_ARABE=[ "=", "'", "b", "p", "t", "_t", "^g", "^c", ".h", "_h",
                       "d", "_d", "r", "z", "^z", "s", "^s", ".s", ".d",
                       ".t", ".z", "`", ".g", "f", "q", "k", "g", "^n",
                       "l", "m", "n", "w", "h", "y" ]

def cfr_radici_arabe(S1,S2):
    def p(s):
        n=0
        l=[]
        while n<len(s):
            ch=s[n]
            if ch in SWITCHES:
                ch=s[n:n+2]
            try:
                l.append(LETTERE_RADICI_ARABE.index(ch))
            except ValueError, e:
                print s,ch
                sys.exit()
            n+=len(ch)
        return(l)
    L1=p(S1)
    L2=p(S2)

    N=min(len(L1),len(L2))

    for n in range(0,N):
        if L1[n]<L2[n]: return(-1)
        if L1[n]>L2[n]: return(1)
        
    if len(L1)<len(L2): return(-1)
    if len(L1)>len(L2): return(-1)

    return(0)
