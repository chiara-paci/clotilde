# -*- coding: utf-8 -*-

from config import *

import re

class Radice(object):
    def __init__(self,radice):
        self.regexp="^"+radice.replace("^","\^").replace("|","\|")
        self.text=radice
        self.re=re.compile(self.regexp)

    def __str__(self): return(self.text)

    def replace(self,base,rep): return(self.text.replace(base,rep))

    def __add__(self,other):
        if type(other)==str:
            return(self.text+other)
        return(self.text+other.text)

    def __radd__(self,other):
        if type(other)==str:
            return(other+self.text)
        return(other.text+self.text)

    def __eq__(self,other):
        if type(other)==str:
            return(other==self.text)
        return(self.text==other.text)

    def __hash__(self): return(hash(self.text))


