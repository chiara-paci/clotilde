# -*- coding: utf-8 -*-

from config import *

class GMatch(object):
    def __init__(self,tipo,order=0,level=0):
        self.tipo=tipo
        self.order=order
        self.level=level

    def __str__(self):
        return(self.tipo)

    def __gt__(self,other):
        if self.order!=other.order:
            return(self.order>other.order)
        return(self.level>other.level)

    def __lt__(self,other): return(other.__gt__(self))

    def __le__(self,other):
        return( (self.__eq__(other) or self.__lt__(other)) )

    def __ge__(self,other):
        return( (self.__eq__(other) or self.__gt__(other)) )

    def __eq__(self,other):
        return( ((self.order==other.order) and (self.level==other.level)) )

    def __ne__(self,other): return(not(self.__eq__(other)))

    def loc_gt(self,other): return(False)

class GMatchSimil(GMatch):
    def __init__(self,level):
        GMatch.__init__(self,"simil",order=10,level=level)

    def __str__(self):
        return(self.tipo+":"+str(self.level))

class GMatchRadice(GMatch):
    def __init__(self,level):
        GMatch.__init__(self,"radice",level=level)

class GMatchPrefix(GMatch):
    def __init__(self,level,altro):
        GMatch.__init__(self,"prefix",level=level)
        self.altro=altro

