import collections.abc
import collections

class FailedUnification(Exception): pass

class Description(collections.abc.MutableMapping):
    def __init__(self,**kwargs):
        self._dict=kwargs

    def __contains__(self,k): return self._dict.__contains__(k)
    def __len__(self): return self._dict.__len__()
    def __iter__(self): return self._dict.__iter__()
    def __getitem__(self,k): return self._dict.__getitem__(k)
    def __delitem__(self,k): return self._dict.__delitem__(k)
    def __setitem__(self,k,v): return self._dict.__setitem__(k,v)
    def keys(self): return self._dict.keys()

    def __str__(self):
        keys=list(self.keys())
        keys.sort()
        S=",".join( [ "%s:%s" % (k,str(self._dict[k])) for k in keys ] )
        return S

    def __hash__(self):
        return hash(self.__str__())

    def html(self,inner=False):
        #S=str(self._dict)
        S=""
        for k in self._dict:
            r='<mtd columnalign="center"><mi>%s</mi></mtd>' % k
            r+='<mtd columnalign="center"><mo>=</mo></mtd>'
            if isinstance(self._dict[k],Description):
                r+='<mtd columnalign="center">%s</mtd>' % self._dict[k].html(inner=True)
            else:
                r+='<mtd columnalign="center"><mn>%s</mn></mtd>' % str(self._dict[k])
            S+="<mtr>%s</mtr>" % r
        S="<mrow><mo>[</mo><mtable>%s</mtable><mo>]</mo></mrow>" % S
        if not inner:
            S="<math>%s</math>" % S
        return S

    def copy(self):
        D=self._dict.copy()
        for k in D:
            if isinstance(D[k],Description):
                D[k]=D[k].copy()
        return Description(**D)

    def __eq__(self,other):
        if not isinstance(other,Description): return NotImplemented
        s_k=list(self.keys())
        o_k=list(other.keys())
        s_k.sort()
        o_k.sort()
        if s_k!=o_k: return False
        for k in s_k:
            if self[k]!=other[k]: return False
        return True

    def __le__(self,other):
        if not isinstance(other,Description): return NotImplemented
        for k in self:
            if k not in other: return False
            if isinstance(self[k],Description):
                if not isinstance(other[k],Description): return False
                if self[k]<=other[k]: continue
                return False
            if isinstance(other[k],Description): return False
            if self[k]!=other[k]: return False
        return True

    def __ge__(self,other):
        if not isinstance(other,Description): return NotImplemented
        return other.__le__(self)

    def __lt__(self,other):
        if not isinstance(other,Description): return NotImplemented
        if self.__eq__(other): return False
        return self.__le__(other)

    def __gt__(self,other):
        if not isinstance(other,Description): return NotImplemented
        if self.__eq__(other): return False
        return self.__ge__(other)

    def __ne__(self,other):
        if not isinstance(other,Description): return NotImplemented
        return not self.__eq__(other)

    def __and__(self,other):
        if not isinstance(other,Description): return NotImplemented

        D=self.copy()
        for k in other:
            if k not in self:
                if isinstance(other[k],Description):
                    D[k]=other[k].copy()
                else:
                    D[k]=other[k]
                continue
            if isinstance(D[k],Description):
                if not isinstance(other[k],Description):
                    raise FailedUnification("conflict on key %s" % k)
                D[k]=D[k].__and__(other[k])
                continue
            if isinstance(other[k],Description):
                raise FailedUnification("conflict on key %s" % k)
            if D[k]!=other[k]:
                raise FailedUnification("conflict on key %s" % k)

        return D
        
    
    #__contains__, __iter__, __len__
    #__le__, __lt__, __eq__, __ne__, __gt__, __ge__, __and__, __or__, __sub__, __xor__, and isdisjoint
    # A < B == A.issubset(B)
