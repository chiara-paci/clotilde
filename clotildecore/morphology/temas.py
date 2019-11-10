from base import descriptions
 
class Tema(descriptions.BaseDescription):
                      
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
        

