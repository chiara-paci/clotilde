# -*- coding: utf-8 -*-

from unittest import skip
from unittest import mock

import random

from base.tests import common as base_common
from . import common
from .. import temas

class TemaTest(common.BaseTestCase,base_common.CommonDescriptionTestCase):
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
        return temas.Tema(**kwargs)

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
