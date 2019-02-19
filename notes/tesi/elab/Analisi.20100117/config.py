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
          [ "h","T","_T",":T",".T","_H",":H",".H","^H","H" ],
          [ "y","I",".I",":I",".E","Y",".Y",":Y", "_Y" ] ]

HARAKAT=[ [ "a", ":a", "^a", "^r" ],
          [ "e", ".e", ":i", "i", "^i" ],
          [ "o", ":o", "u", ":u", "uN" ] ]

NUN_SIGN="N"
IZAFET_SIGN="-"

HARAKAT_IND={ "a": 0, "i": 1, "u": 2 }

HAMZA=[ "'", "^o" ]


HARAKAT_TUTTE=reduce(lambda x,y: x+y,HARAKAT)
LETTERE_TUTTE=reduce(lambda x,y: x+y,LETTERE)

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
                "PT": "persiano-turco",
                "TA": "turco-arabo",
                "TP": "turco-persiano",
                "num": "numero",
                "n": "nome",
                "v": "verbo",
                "va": "verbo ausiliario",
                "np": "nome proprio",
                "loc": "locuzione",
                "agg": "aggettivo",
                "aggc": "agg. comparativo",
                "aggs": "agg. superlativo",
                "aggn": "agg. numerale",
                "avv": "avverbio",
                "cong": "congiunzione",
                "pron": "pronome",
                "post": "postposizione",
                "int": "interiezione" }

GRAMMATICALI={ "va": "Verbi ausiliari",
               "pron" : "Pronomi",
               "num" : "Numeri",
               "aggn": "Aggettivi numerali",
               "np": "Nomi Propri",
               "post": "Post e preposizioni",
               "cong" : "Congiunzioni" }

ORDINE_GRAMMATICALI=[ "np", "va", "pron", "post", "cong", "num", "aggn" ]

FONTI_PRONUNCIA={ "redhouse1997": ("cont",1.0),
                  "timurtas1999": ("cont",1.0),
                  "kiefferbianchi18351": ("cont",0.50)}

COLORA={ "nonorigine": True,
         "nonref": True,
         "nonrefpron": False,
         "nosignificato": True }

COLORI_ORDINE=[ "nosignificato", "nonorigine", "nonrefpron", "nonref" ]


COLORI={ "nonorigine": (0.8,0.4,0),
         "nonref": (0.5,0,0.5),
         "nonrefpron": (1,0,1),
         "nosignificato": (1,0,0),
         "sologlossario": (0.5,0.5,0.5),
         "solodoc": (0,0.5,0) }

def spzrl(S):
    if S[0]!="{":
        return("\\spzrl{"+S+"}")
    return("\\spzrl"+S)
    
