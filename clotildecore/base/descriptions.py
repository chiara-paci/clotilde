import collections.abc

class Description(collections.abc.Set):
    def __init__(self,**kwargs):
        self._dict=kwargs

    #__contains__, __iter__, __len__
    #__le__, __lt__, __eq__, __ne__, __gt__, __ge__, __and__, __or__, __sub__, __xor__, and isdisjoint
    # A < B == A.issubset(B)
