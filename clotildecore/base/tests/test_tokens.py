# -*- coding: utf-8 -*-

from unittest import skip
from unittest import mock

import random

from . import common
from .. import tokens

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
        new_lines=random.choices(tokens.NEW_LINES,k=num_breaks)
        
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
    def create_random_object(self):
        return self.create_object(self.random_string(with_spaces=False),
                                  self.random_string(),
                                  self.random_description())

    def create_object(self,label,text,description,final=None):
        if final is None:
            return tokens.Token(label,text,description)
        return tokens.Token(label,text,description,final=final)
        
    def make_parameters(self,label,text,description,final=None):
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

    def test_method_html(self):
        label=self.random_string(with_spaces=False)
        text=self.random_string()
        description=self.random_description()
        self._test_method_html(label,text,description)

    def test_object_is_hashable(self):
        label=self.random_string(with_spaces=False)
        text=self.random_string()
        description=self.random_description()
        self._test_object_is_hashable(label,text,description)

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


    
