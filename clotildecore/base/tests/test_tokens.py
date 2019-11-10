# -*- coding: utf-8 -*-

from unittest import skip
from unittest import mock

import random

from . import common
from .. import tokens,descriptions

class ConstantTest(common.BaseTestCase):
    def test_tokens_constant(self):
        for name,required,actual in [ 
                ("MARKERS",self.CONST_TOKENS["MARKERS"],tokens.MARKERS),
                ("NEW_LINES",self.CONST_TOKENS["NEW_LINES"],tokens.NEW_LINES),
        ]: 
            for n in range(0,len(required)):
                with self.subTest(const=name,n=n):
                    self.assertConstant(name,required[n],actual[n])
                    
class FunctionTest(common.BaseTestCase):
    def test_function_replace_newline(self):
        N=random.randint(100,1000)
        S=self.random_string(size=N)

        num_breaks=random.randint(2,10)
        breaks=[]
        while len(breaks)<num_breaks:
            n=random.randint(101,N-2)
            if n in breaks: continue
            breaks.append(n)
        breaks.sort()

        t=[]
        for n in range(0,num_breaks):
            if n==0:
                t.append(S[:breaks[n]])
                continue
            t.append(S[breaks[n-1]:breaks[n]])
        t.append(S[breaks[-1]:])

        repl=self.random_string()
        new_lines=self.random_choices(tokens.NEW_LINES,k=num_breaks)
        
        t_data=[]
        t_exp_true=[]
        t_exp_false=[]
        for n in range(0,num_breaks):
            t_data.append(t[n])
            t_exp_true.append(t[n])
            t_exp_false.append(t[n])
            t_data.append(new_lines[n][1])
            t_exp_true.append(new_lines[n][0])
            t_exp_true.append(repl)
            t_exp_false.append(repl)
        t_data.append(t[-1])
        t_exp_true.append(t[-1])
        t_exp_false.append(t[-1])
        
        S_data="".join(t_data)
        S_exp_true="".join(t_exp_true)
        S_exp_false="".join(t_exp_false)

        with self.subTest(preserve=True):
            self.assertFunctionCall(S_exp_true,tokens.replace_newline,S_data,repl,preserve=True)
        with self.subTest(preserve=False):
            self.assertFunctionCall(S_exp_false,tokens.replace_newline,S_data,repl,preserve=False)
        with self.subTest(preserve="default"):
            self.assertFunctionCall(S_exp_false,tokens.replace_newline,S_data,repl)

class TokenTest(common.BaseTestCase,common.CommonTokenTestCase):
    def create_object(self,label,text,description,final=None):
        if final is None:
            return tokens.Token(label,text,description)
        return tokens.Token(label,text,description,final=final)

    def create_random_parameters(self):
        label=self.random_string(with_spaces=False)
        text=self.random_string()
        description=self.random_description()
        return [label,text,description],{}

    def expected_attributes(self,label,text,description,final=None):
        t=text.replace('\xa0'," ") # non breaking space
        t=tokens.replace_newline(t,"¶")
        if final is None:
            return label,t,description,False
        return label,t,description,final
    
    def test_attribute_values(self):
        label=self.random_string(with_spaces=False)
        text=self.random_string()
        description=self.random_description()
        with self.subTest(final=None):
            self._test_attribute_values(label,text,description)
        with self.subTest(final=True):
            self._test_attribute_values(label,text,description,final=True)
        with self.subTest(final=False):
            self._test_attribute_values(label,text,description,final=False)

    def test_object_is_sortable(self):
        N=random.randint(2,10)
        p_list=[]
        for n in range(0,N):
            label=self.random_string(with_spaces=False)
            text1=self.random_string()
            description1=self.random_description()
            text2=self.random_string()
            description2=self.random_description()
            p_list.append( ( (label,text1,description1), {} ) )
            p_list.append( ( (label,text2,description1), {} ) )
            p_list.append( ( (label,text1,description2), {} ) )
            p_list.append( ( (label,text2,description2), {} ) )
        self._test_object_is_sortable(p_list)

class TokenBaseTest(common.BaseTestCase,common.CommonTokenTestCase):
    def create_object(self,label,text,final=None):
        if final is None:
            return tokens.TokenBase(label,text)
        return tokens.TokenBase(label,text,final=final)

    def create_random_parameters(self):
        label=self.random_string(with_spaces=False)
        text=self.random_string()
        return [label,text],{}

    def expected_attributes(self,label,text,final=None):
        t=text.replace('\xa0'," ") # non breaking space
        t=tokens.replace_newline(t,"¶")
        description=descriptions.Description(base=label)
        if final is None:
            return label,t,description,False
        return label,t,description,final
    
    def test_attribute_values(self):
        label=self.random_string(with_spaces=False)
        text=self.random_string()
        with self.subTest(final=None):
            self._test_attribute_values(label,text)
        with self.subTest(final=True):
            self._test_attribute_values(label,text,final=True)
        with self.subTest(final=False):
            self._test_attribute_values(label,text,final=False)

    def test_object_is_sortable(self):
        N=random.randint(2,10)
        p_list=[]
        for n in range(0,N):
            label1=self.random_string(with_spaces=False)
            label2=self.random_string(with_spaces=False)
            text1=self.random_string()
            text2=self.random_string()
            p_list.append( ( (label1,text1), {} ) )
            p_list.append( ( (label1,text2), {} ) )
            p_list.append( ( (label2,text1), {} ) )
            p_list.append( ( (label2,text2), {} ) )
        self._test_object_is_sortable(p_list)

class TokenNotFoundTest(common.BaseTestCase,common.CommonTokenTestCase):
    def create_object(self,text):
        return tokens.TokenNotFound(text)

    def create_random_parameters(self):
        text=self.random_string()
        return [text],{}

    def expected_attributes(self,text):
        t=text.replace('\xa0'," ") # non breaking space
        t=tokens.replace_newline(t,"¶")
        label="not-found"
        description=descriptions.Description(base=label)
        final=True
        return label,t,description,final
    
    def test_attribute_values(self):
        text=self.random_string()
        self._test_attribute_values(text)

    def test_object_is_sortable(self):
        N=random.randint(2,10)
        p_list=[]
        for n in range(0,N):
            flag=self.random_boolean()
            text=self.random_string()
            p_list.append( ( (text,), {} ) )
            if flag:
                p_list.append( ( (text,), {} ) )
        self._test_object_is_sortable(p_list)

class TokenMarkerTest(common.BaseTestCase,common.CommonTokenTestCase):
    def create_object(self,marker,pos):
        return tokens.TokenMarker(marker,pos)

    def create_random_parameters(self):
        marker=self.random_choices(tokens.MARKERS)
        pos=self.random_choices(["begin","end"])
        return [marker,pos],{}

    def _mark(self,marker):
        if marker not in tokens.MARKERS: return ""
        if marker in ["center","left","right"]:
            return '<i class="fas fa-align-%s"></i>' % marker
        return '<i class="fas fa-italic"></i>'
    
    def expected_attributes(self,marker,pos):
        if marker in tokens.MARKERS:
            label="marker"
        else:
            label="not-found"
        description=descriptions.Description(base=label)
        final=True
        if pos=="begin":
            text='<i class="fas fa-arrow-alt-circle-right"></i>'
            text+=self._mark(marker)
        else:
            text=self._mark(marker)
            text+='<i class="fas fa-arrow-alt-circle-left"></i>'
        return label,text,description,final
    
    def test_attribute_values(self):
        markers=[ self.random_choices([ m for m in tokens.MARKERS if m!="i" ]),
                  "i",self.random_string() ]
        pos=[ "begin",self.random_string() ]
        for m in markers:
            for p in pos:
                with self.subTest(marker=m,pos=p):
                    self._test_attribute_values(m,p)


    def test_object_is_sortable(self):
        markers=tokens.MARKERS + [ self.random_string() ]
        pos=[ "begin",self.random_string() ]
        p_list=[]
        N=random.randint(2,10)
        for n in range(0,N):
            m1=self.random_choices(markers)
            m2=self.random_choices(markers)
            p1=self.random_choices(pos)
            p2=self.random_choices(pos)
            p_list.append( ( (m1,p1), {} ) )
            p_list.append( ( (m1,p2), {} ) )
            p_list.append( ( (m2,p1), {} ) )
            p_list.append( ( (m2,p2), {} ) )
        self._test_object_is_sortable(p_list)

