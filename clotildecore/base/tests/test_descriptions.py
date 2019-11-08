# -*- coding: utf-8 -*-

from unittest import skip
from unittest import mock

import random

from . import common
from .. import descriptions

class ExceptionTest(common.BaseTestCase):
    def test_tokens_exception(self):
        obj=descriptions.FailedUnification(self.random_string())
        self.assertIsInstance(obj,Exception)

class DescriptionTest(common.BaseTestCase,common.CommonDescriptionTestCase):
    def value_to_str(self,val):
        if type(val) in [tuple,list]:
            if not val[1]:
                return str(val[0])
            return '!%s' % str(val[0])
        return str(val)

    def create_random_value(self):
        #return (self.random_string(),self.random_boolean())
        return (self.random_string(),True)

    def create_object(self,**kwargs):
        return descriptions.Description(**kwargs)

    def test_operator_lt(self): assert True   # A<B
    def test_operator_gt(self): assert True   # A>B
    def test_operator_eq(self): assert True   # A==B
    def test_operator_ne(self): assert True   # A!=B
    def test_operator_le(self): assert True   # A<B
    def test_operator_ge(self): assert True   # A>B

class TemaTest(common.BaseTestCase,common.CommonDescriptionTestCase):
    def value_to_str(self,val):
        if type(val) not in [list,set]:
            return str(val)
        V=list(val)
        V.sort()
        return '[%s]' % ",".join([ str(v) for v in V ])

    def create_random_value(self):
        if self.random_boolean():
            return self.random_string() # string
        N=random.randint(2,10) 
        return set([ self.random_string() for n in range(0,N) ]) # list

    def create_object(self,**kwargs):
        return descriptions.Tema(**kwargs)

    def test_operator_plus_incoherent(self): 
        kwargs1,kwargs2=self.create_two_kwargs_incoherent()
        obj1=self.create_object(**kwargs1)
        obj2=self.create_object(**kwargs2)
        obj_sum=obj1+obj2
        for k in kwargs1:
            with self.subTest(case="k in A",k=k):
                self.assertIn(k,obj_sum)
                self.assertIsDescriptionSubset(kwargs1[k],obj_sum[k])
        for k in kwargs2:
            with self.subTest(case="k in B",k=k):
                self.assertIn(k,obj_sum)
                self.assertIsDescriptionSubset(kwargs2[k],obj_sum[k])

