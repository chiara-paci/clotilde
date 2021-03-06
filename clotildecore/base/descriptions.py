import collections.abc
import collections

class FailedUnification(Exception): pass

class BaseDescription(collections.abc.MutableMapping):
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
        S=",".join( [ "%s:%s" % (k,self._str_value(self._dict[k])) for k in keys ] )
        return S

    def html(self,inner=False):
        S=""
        keys=list(self.keys())
        keys.sort()
        for k in keys:
            r='<mtd columnalign="center"><mi>%s</mi></mtd>' % k
            r+='<mtd columnalign="center"><mo>=</mo></mtd>'
            r+='<mtd columnalign="center"><mn>%s</mn></mtd>' % self._str_value(self._dict[k])
            S+="<mtr>%s</mtr>" % r
        S="<mrow><mo>[</mo><mtable>%s</mtable><mo>]</mo></mrow>" % S
        if not inner:
            S="<math>%s</math>" % S
        return S

    
    def __hash__(self):
        return hash(self.__str__())

    def __ge__(self,other):
        if type(other) is not type(self): return NotImplemented
        return other.__le__(self)

    def __lt__(self,other):
        if type(other) is not type(self): return NotImplemented
        if self.__eq__(other): return False
        return self.__le__(other)

    def __gt__(self,other):
        if type(other) is not type(self): return NotImplemented
        if self.__eq__(other): return False
        return self.__ge__(other)

    def __ne__(self,other):
        if type(other) is not type(self): return NotImplemented
        return not self.__eq__(other)

    def copy(self):
        D=self._dict.copy()
        return type(self)(**D)
    

    
## A Description object can   have negative values but can't have multiple values.
## A Tema        object can't have negative values but can   have multiple values.

class Description(BaseDescription):

    def _str_value(self,val):
        if type(val) in [tuple,list]:
            if not val[1]:
                return str(val[0])
            return '!%s' % str(val[0])
        return str(val)
    
    def __eq__(self,other):
        if not isinstance(other,Description): return NotImplemented
        s_k=list(self.keys())
        o_k=list(other.keys())
        s_k.sort()
        o_k.sort()
        if s_k!=o_k: return False
        for k in s_k:
            if self._cfr(self[k],other[k])!=0: return False
        return True

    # This is a "contains" confrontation, so _cfr(a,b)=1 is a !< b and not a>b
    def _cfr(self,a,b):
        if type(a) is tuple:
            a_val,a_neg=a
        else:
            a_val=a
            a_neg=False

        if type(b) is tuple:
            b_val,b_neg=b
        else:
            b_val=b
            b_neg=False

        if a_val==b_val and a_neg==b_neg: return 0
        if a_val!=b_val and a_neg!=b_neg: return -1
        return 1

    def _match(self,a,b):
        if type(a) is tuple:
            a_val,a_neg=a
        else:
            a_val=a
            a_neg=False

        if type(b) is tuple:
            b_val,b_neg=b
        else:
            b_val=b
            b_neg=False

        if a_val==b_val and a_neg==b_neg: return True
        if a_val!=b_val and a_neg!=b_neg: return True
        return False

    
    def __le__(self,other):
        if type(other) is not type(self): return NotImplemented
        for k in self:
            if k not in other: 
                if type(self[k]) is not tuple: return False
                if self[k][1]: continue
                return False
            #if self._cfr(self[k],other[k])<=0: continue
            if self._match(self[k],other[k]): continue
            return False
        return True

    def __add__(self,other):
        if type(other) is not type(self): return NotImplemented

        D=self.copy()
        for k in other:
            if k not in self:
                D[k]=other[k]
                continue
            if D[k]!=other[k]:
                raise FailedUnification("conflict on key %s" % k)

        return D


class Tema(BaseDescription):
                      
    def _str_value(self,val):
        if type(val) not in [list,set]:
            return str(val)
        V=list(val)
        V.sort()
        return '[%s]' % ",".join([ str(v) for v in V ])

    def __eq__(self,other):
        if type(other) is not type(self): return NotImplemented
        s_k=list(self.keys())
        o_k=list(other.keys())
        s_k.sort()
        o_k.sort()
        if s_k!=o_k: return False
        for k in s_k:
            if self._cfr(self[k],other[k])!=0: return False
        return True

    def _cfr(self,a,b):
        if type(a) is set:
            a_set=a
        elif type(a) is list: 
            a_set=set(a)
        else:
            a_set=set([a])

        if type(b) is set:
            b_set=b
        elif type(b) is list: 
            b_set=set(b)
        else:
            b_set=set([b])

        if a_set==b_set: return 0
        if a_set<b_set: return -1
        return 1

    def __le__(self,other):
        if type(other) is not type(self): return NotImplemented
        for k in self:
            if k not in other: return False
            if self._cfr(self[k],other[k])<=0: continue
            return False
        return True

    def _value_add(self,v1,v2):
        ret=set()
        if type(v1) in [set,list]:
            ret=ret.union(v1)
        else:
            ret.add(v1)
        if type(v2) in [set,list]:
            ret=ret.union(v2)
        else:
            ret.add(v2)
        if len(ret)>1: return ret
        return ret.pop()

    def __add__(self,other):
        if type(other) is not type(self): return NotImplemented
        D=self.copy()
        for k in other:
            if k not in self:
                D[k]=other[k]
                continue
            D[k]=self._value_add(D[k],other[k])
        return D
        
    
    #__contains__, __iter__, __len__
    #__le__, __lt__, __eq__, __ne__, __gt__, __ge__, __and__, __or__, __sub__, __xor__, and isdisjoint
    # A < B == A.issubset(B)
