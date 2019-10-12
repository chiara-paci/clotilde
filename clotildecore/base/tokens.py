# -*- coding: utf-8 -*-

from . import descriptions

MARKERS=[ u"center",u"right",u"i",u"left"]

NEW_LINES=[('RN',   '\r\n'),
           ('NR',   '\n\r'),
           ('N',    '\n'),
           ('XB',   '\x0b'),
           ('XC',   '\x0c'),
           ('R',    '\r'),
           ('X85',  '\x85'),
           ('X2028',chr(0x2028)),
           ('X2029',chr(0x2029))]

def replace_newline(S,repl,preserve=False):
    if not preserve:
        for (r,n) in NEW_LINES:
            S=S.replace(n,repl)
        return(S)
    for (r,n) in NEW_LINES:
        S=S.replace(n,r+repl)
    return(S)

class Token(object):
    def __init__(self,label,text,description,final=False):
        self.label=label
        self.text=self._clean(text)
        self.description=description
        self.final=final

    def _clean(self,t):
        t=t.replace('\xa0'," ") # non breaking space
        t=replace_newline(t,"¶")
        return t

    def html(self):
        T='<span class="token '+self.label+'"> '
        T+=self.text.replace("¶","¶<br/>")
        T+="</span>"
        return T

    def __hash__(self):
        return hash(self.label+":"+self.text+"/"+str(self.description))

    def __eq__(self,other):
        if self.text != other.text: return False
        return self.description == other.description

    def __lt__(self,other):
        if self.text.lower() < other.text.lower(): return True
        if self.text.lower() > other.text.lower(): return False
        return self.description < other.description

    def __le__(self,other): return self.__eq__(other) or self.__lt__(other)
    def __gt__(self,other): return other.__lt__(self)
    def __ge__(self,other): return self.__eq__(other) or self.__gt__(other)
    def __ne__(self,other): return not self.__eq__(other)

class TokenBase(Token):
    def __init__(self,label,text,final=False):
        Token.__init__(self,label,text,
                       descriptions.Description(base=label),
                       final=final)


class TokenMarker(TokenBase):
    def __init__(self,marker,pos):
        self._marker=marker
        self._pos=pos
        if self._pos=="begin":
            text='<i class="fas fa-arrow-alt-circle-right"></i>'
            text+=self._mark()
        else:
            text=self._mark()
            text+='<i class="fas fa-arrow-alt-circle-left"></i>'

        if self._marker not in MARKERS:
            label="not-found"
        else:
            label="marker"
        TokenBase.__init__(self,label,text,True)

    def _clean(self,t): return t

    def _mark(self):
        if self._marker not in MARKERS: return ""
        if self._marker in ["center","left","right"]:
            return '<i class="fas fa-align-%s"></i>' % self._marker
        return '<i class="fas fa-italic"></i>'

class TokenNotFound(TokenBase):
    def __init__(self,text):
        TokenBase.__init__(self,"not-found",text,True)
