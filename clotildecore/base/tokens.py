# -*- coding: utf-8 -*-

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
    def __init__(self,label,text):
        self._label=label
        self._text=self._clean(text)

    def _clean(self,t):
        t=t.replace('\xa0'," ") # non breaking space
        t=replace_newline(t,"¶<br/>")
        return t

    def html(self):
        T='<span class="token '+self._label+'"> '
        T+=self._text
        T+="</span>"
        return T

class TokenMarker(Token):
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
        Token.__init__(self,label,text)

    def _clean(self,t): return t

    def _mark(self):
        if self._marker not in MARKERS: return ""
        if self._marker in ["center","left","right"]:
            return '<i class="fas fa-align-%s"></i>' % self._marker
        return '<i class="fas fa-italic"></i>'

        

class TokenNotFound(Token):
    def __init__(self,text):
        Token.__init__(self,"not-found",text)
