# -*- coding: utf-8 -*-

from django.test import TestCase
from django.db.utils import IntegrityError
from sqlite3 import IntegrityError as S3IntegrityError

import random
import string
import abc

from .. import models
from .. import descriptions

class CommonTestCase(TestCase):

    def random_string(self,size=0,with_spaces=True,max_size=10,min_size=3,only_chars="",add_chars=""):
        if not size:
            size=random.choice(range(min_size,max_size))
        if only_chars:
            chars=only_chars
        else:
            chars=string.ascii_lowercase +string.ascii_uppercase + string.digits
            chars+=add_chars
            if with_spaces:
                chars+="    "
        S=''.join(random.choice(chars) for _ in range(size))
        if with_spaces:
            S=S.strip()
            S=" ".join(S.split())
        return S

    def random_boolean(self):
        return random.randint(1,10)>5

    def random_dict(self):
        N=random.randint(1,10)
        return { self.random_string(): self.random_string() for n in range(0,N) }

    def random_description(self):
        return descriptions.Description(**self.random_dict())

    def random_choices(self,seq,k=1):
        try:
            vals=random.choices(seq,k=k) # Python >= 3.6
        except AttributeError as e:
            vals=[]
            for n in range(0,k):
                ind=random.choice(range(0,len(seq)))
                vals.append(seq[ind])
        return vals
    
    def assertHasAttribute(self,obj,attr):
        self.assertTrue(hasattr(obj,attr),
                        msg="Object '%s' of class %s has no attribute '%s'" % (obj, obj.__class__,attr) )

    def assertIsCallable(self,func):
        self.assertTrue(hasattr(func,"__call__"),
                        msg="Object '%s' is not callable" % str(func))

    def assertHasMethod(self,obj,attr):
        self.assertHasAttribute(obj,attr)
        self.assertIsCallable(getattr(obj,attr))

    def assertConstant(self,name,required,actual):
        self.assertEqual(required,actual,
                         msg="Constant %s: required='%s', actual='%s'" % (name,required,actual))

    def assertFunctionCall(self,expected,func,*args,**kwargs):
        actual=func(*args,**kwargs)
        self.assertEqual(expected,actual,
                         msg="Wrong return value for '%s': expected='%s', actual='%s' " % (func.__name__,
                                                                                           str(expected),
                                                                                           str(actual)))

    def assertToken(self,obj,cls,label,text,final):
        self.assertIsInstance(obj,cls)
        self.assertEqual(obj.text,text)
        self.assertEqual(obj.label,label)
        self.assertEqual(obj.final,final)

    def assertUnique(self,create_func,*args,**kwargs):
        obj=create_func(*args,**kwargs)
        with self.assertRaises( (IntegrityError,) ):
            obj=create_func(*args,**kwargs)

    def assertIsCopy(self,obj_1,obj_2):
        self.assertEqual(obj_1,obj_2)
        self.assertIsNot(obj_1,obj_2)

    def assertIsDescriptionSubset(self,val1,val2):
        if type(val2) is str:
            self.assertIs(type(val1),str,msg="%s is not description subset of %s" % (val1,val2) )
            self.assertEqual(val1,val2,msg="%s is not description subset of %s" % (val1,val2) )
            return
        if type(val2) is set:
            S2=val2
        else:
            S2=set(val2)
        if type(val1) is set:
            self.assertTrue(val1.issubset(S2),msg="%s is not description subset of %s" % (val1,val2) )
            return
        if type(val1) is list:
            self.assertTrue(set(val1).issubset(S2),msg="%s is not description subset of %s" % (val1,val2) )
            return
        self.assertIn(val1,S2,msg="%s is not description subset of %s" % (val1,val2) )

        
class BaseTestCase(CommonTestCase): 
    app_name="base"
    
    CONST_MODELS={
        "ALPHA": 'a-zA-ZàèìòùáéíóúÀÈÌÒÙÁÉÍÓÚ',
        "ALPHA_ORDER": "AaÁáÀàÄäÆæ;Bb;CcÇç;Dd;EeÈèÉéËë;Ff;Gg;Hh;Ii;Jj;Kk;Ll;Mm;OoÒòÓóÖöŒœ;Pp;Qq;Rr;SsŞş;Tt;UuÙùÚúÜü;Vv;Ww;Xx;Yy;Zz",
        "DEFAULT_DESCRIPTION_NAME":"vuota",
    }

    CONST_TOKENS={
        "MARKERS": [ "center","right","i","left"],
        "NEW_LINES": [('RN',   '\r\n'),
                      ('NR',   '\n\r'),
                      ('N',    '\n'),
                      ('XB',   '\x0b'),
                      ('XC',   '\x0c'),
                      ('R',    '\r'),
                      ('X85',  '\x85'),
                      ('X2028',chr(0x2028)),
                      ('X2029',chr(0x2029))],
    }


    def create_casepair(self,lower,upper):
        return models.CasePair.objects.create(lower=lower,upper=upper)

    def create_random_casepair(self):
        return self.create_casepair(lower=self.random_string(),upper=self.random_string())

    def create_caseset(self,name):
        return models.CaseSet.objects.create(name=name)

    def create_random_caseset(self):
        return self.create_caseset(name=self.random_string())

    def create_tokenregexp(self,name,regexp=None):
        if regexp is None:
            return models.TokenRegexp.objects.create(name=name)
        return models.TokenRegexp.objects.create(name=name,regexp=regexp)

    def create_random_tokenregexp(self):
        return self.create_tokenregexp(name=self.random_string())

    def create_tokenregexpset(self,name):
        return models.TokenRegexpSet.objects.create(name=name)

    def create_random_tokenregexpset(self):
        return self.create_tokenregexpset(name=self.random_string())

    def create_tokenregexpsetthrough(self,regexp_set,regexp,order,disabled=None,
                                     bg_color=None,fg_color=None,final=None):
        kwargs={}
        if bg_color is not None:
            kwargs["bg_color"]=bg_color
        if fg_color is not None:
            kwargs["fg_color"]=fg_color
        if final is not None:
            kwargs["final"]=final
        if disabled is not None:
            kwargs["disabled"]=disabled
        return models.TokenRegexpSetThrough.objects.create(token_regexp_set=regexp_set,token_regexp=regexp,
                                                           order=order,**kwargs)

    def create_random_tokenregexpsetthrough(self):
        token_regexp_set=self.create_random_tokenregexpset()
        token_regexp=self.create_random_tokenregexp()
        order=random.randint(0,10)
        return self.create_tokenregexpsetthrough(token_regexp_set,token_regexp,order)

    def create_alphabeticorder(self,name,order=None):
        if order is None:
            return models.AlphabeticOrder.objects.create(name=name)
        return models.AlphabeticOrder.objects.create(name=name,order=order)

    def create_random_alphabeticorder(self):
        return self.create_alphabeticorder(self.random_string())

    def create_attribute(self,name,order=None):
        if order is None:
            return models.Attribute.objects.create(name=name)
        return models.Attribute.objects.create(name=name,order=order)

    def create_random_attribute(self):
        return self.create_attribute(self.random_string())

    def create_value(self,s,order=None,variable=None):
        kwargs={}
        if order is not None:
            kwargs["order"]=order
        if variable is not None:
            kwargs["variable"]=variable
        return models.Value.objects.create(string=s,**kwargs)

    def create_random_value(self):
        return self.create_value(self.random_string())

    def create_entry(self,attr,val,invert=None):
        if invert is None:
            return models.Entry.objects.create(attribute=attr,value=val)
        return models.Entry.objects.create(attribute=attr,value=val,invert=invert)

    def create_random_entry(self):
        return self.create_entry(self.create_random_attribute(),self.create_random_value())

    def create_description(self,name):
        return models.Description.objects.create(name=name)

    def create_random_description(self):
        return self.create_description(name=self.random_string())

class CommonModelTestCase(abc.ABC):
    fields_default=[]
    
    @property
    @abc.abstractmethod
    def fields(self): return []
        
    @property
    @abc.abstractmethod
    def model_name(self): return ""
        
    @abc.abstractmethod
    def create_random_object(self): return None

    @abc.abstractmethod
    def correct_str(self): return ""

    def test_object_has_fields(self):
        obj=self.create_random_object()
        for f in self.fields:
            with self.subTest(field=f):
                self.assertHasAttribute(obj,f)

    def test_fields_default(self):
        obj=self.create_random_object()
        for f,default in self.fields_default:
            msg_format="Wrong default for field '%s': expected '%s', actual '%s'" 
            with self.subTest(field=f):
                self.assertEqual(getattr(obj,f),default,
                                 msg = msg_format % (f,default,getattr(obj,f)) )

    def test_str(self):
        obj=self.create_random_object()
        correct_str=self.correct_str(obj)
        self.assertEqual(str(obj),correct_str)

    def test_get_absolute_url(self):
        obj=self.create_random_object()
        correct_url="/%s/%s/%d" % (self.app_name,self.model_name,obj.pk)
        self.assertEqual(obj.get_absolute_url(),correct_url)

class CommonTokenTestCase(abc.ABC):
    attributes=["label","text","description","final"]
    
    @abc.abstractmethod
    def create_object(self,*args,**kwargs):
        return None

    @abc.abstractmethod
    def expected_attributes(self,*args,**kwargs):
        label=""
        text=""
        desc=None
        final=None # boolean
        return label,text,desc,final

    @abc.abstractmethod
    def create_random_parameters(self):
        return [],{}

    def create_random_object(self):
        args,kwargs=self.create_random_parameters()
        return self.create_object(*args,**kwargs)

    def test_object_has_attributes(self):
        obj=self.create_random_object()
        for a in self.attributes:
            with self.subTest(attribute=a):
                self.assertHasAttribute(obj,a)

    def _test_method_html(self,*args,**kwargs):
        obj=self.create_object(*args,**kwargs)
        label,text,desc,final=self.expected_attributes(*args,**kwargs)
        exp_format='<span class="token %s">%s</span>'
        expected=exp_format % ( label, text.replace("¶","¶<br/>"))
        result=obj.html()
        self.assertTrue(expected,result)

    def _test_attribute_values(self,*args,**kwargs):
        obj=self.create_object(*args,**kwargs)
        label,text,desc,final=self.expected_attributes(*args,**kwargs)
        expected={
            "label": label,
            "text": text,
            "description": desc,
            "final": final,
        }

        for a in expected:
            with self.subTest(attribute=a):
                self.assertEqual(expected[a],getattr(obj,a))

        
    def _test_object_is_hashable(self,*args,**kwargs):
        obj=self.create_object(*args,**kwargs)
        label,text,desc,final=self.expected_attributes(*args,**kwargs)
        expected=hash(label+":"+text+"/"+str(desc))
        self.assertFunctionCall(expected,hash,obj)

    def _test_object_is_sortable(self,param_list):
        random.shuffle(param_list)
        obj_list=[]
        expected_list=[]
        for args,kwargs in param_list:
            obj=self.create_object(*args,**kwargs)
            label,text,desc,final=self.expected_attributes(*args,**kwargs)
            expected_list.append( (text.lower(),desc,obj) )
            obj_list.append(obj)
        obj_list.sort()
        expected_list.sort()

        for n in range(0,len(obj_list)):
            with self.subTest(n=n):
                msg="expected: %s %s, actual: %s %s" % (expected_list[n][0],str(expected_list[n][1]),
                                                        obj.text,str(obj.description)) 
                self.assertEqual(obj_list[n],expected_list[n][2],msg=msg)

    def test_method_html(self):
        args,kwargs=self.create_random_parameters()
        self._test_method_html(*args,**kwargs)

    def test_object_is_hashable(self):
        args,kwargs=self.create_random_parameters()
        self._test_object_is_hashable(*args,**kwargs)

class CommonDescriptionTestCase(abc.ABC):
    @abc.abstractmethod
    def value_to_str(self,val): return ""

    @abc.abstractmethod
    def create_random_value(self): return ""

    @abc.abstractmethod
    def create_object(self,**kwargs): return None

    def create_random_kwargs(self,min_len=1,max_len=10):
        N=random.randint(min_len,max_len)
        kwargs={}
        for n in range(0,N):
            key=self.random_string()
            value=self.create_random_value()
            kwargs[key]=value
        return kwargs

    def create_two_kwargs_disjointed(self):
        kwargs1=self.create_random_kwargs(min_len=6,max_len=20)
        kwargs2=self.create_random_kwargs(min_len=6,max_len=20)
        if len(kwargs1)<=len(kwargs2):
            for k in kwargs1:
                if k in kwargs2: del(kwargs2[k])
        else:
            for k in kwargs2:
                if k in kwargs1: del(kwargs1[k])
        return kwargs1,kwargs2

    def create_two_kwargs_overlapping(self):
        kwargs1,kwargs2=self.create_two_kwargs_disjointed()
        q=random.randint(0,1)
        N1=random.randint(q,3)
        N2=random.randint(1-q,3)
        keys1=self.random_choices(list(kwargs1.keys()),k=N1)
        keys2=self.random_choices(list(kwargs2.keys()),k=N2)
        for k in keys1: kwargs2[k]=kwargs1[k]
        for k in keys2: kwargs1[k]=kwargs2[k]
        return kwargs1,kwargs2

    def create_two_kwargs_subset_first(self):
        kwargs1=self.create_random_kwargs(min_len=6,max_len=10)
        kwargs2=self.create_random_kwargs(min_len=6,max_len=10)
        for k in kwargs1:
            kwargs2[k]=kwargs1[k]
        return kwargs1,kwargs2

    def create_two_kwargs_subset_second(self):
        kwargs1=self.create_random_kwargs(min_len=6,max_len=10)
        kwargs2=self.create_random_kwargs(min_len=6,max_len=10)
        for k in kwargs2:
            kwargs1[k]=kwargs2[k]
        return kwargs1,kwargs2

    def create_two_kwargs_incoherent(self):
        kwargs1=self.create_random_kwargs()
        kwargs2=self.create_random_kwargs()
        q=random.randint(0,1)
        N1=random.randint(q,3)
        N2=random.randint(1-q,3)
        keys1=self.random_choices(list(kwargs1.keys()),k=N1)
        keys2=self.random_choices(list(kwargs2.keys()),k=N2)
        for k in keys1: kwargs2[k]=self.create_random_value()
        for k in keys2: kwargs1[k]=self.create_random_value()
        return kwargs1,kwargs2

    def test_copy(self):
        kwargs=self.create_random_kwargs()
        desc=self.create_object(**kwargs)
        desc2=desc.copy()
        self.assertIsCopy(desc,desc2)

    def test_str(self):
        kwargs=self.create_random_kwargs()
        desc=self.create_object(**kwargs)
        keys=list(kwargs.keys())
        keys.sort()
        expected=",".join( [ "%s:%s" % (k,self.value_to_str(kwargs[k])) for k in keys ] )
        self.assertEqual(expected,str(desc))

    def test_html(self):
        kwargs=self.create_random_kwargs()
        desc=self.create_object(**kwargs)
        keys=list(kwargs.keys())
        keys.sort()
        S=""
        for k in keys:
            r='<mtd columnalign="center"><mi>%s</mi></mtd>' % k
            r+='<mtd columnalign="center"><mo>=</mo></mtd>'
            r+='<mtd columnalign="center"><mn>%s</mn></mtd>' % self.value_to_str(kwargs[k])
            S+="<mtr>%s</mtr>" % r
        S="<mrow><mo>[</mo><mtable>%s</mtable><mo>]</mo></mrow>" % S
        expected="<math>%s</math>" % S
        self.assertEqual(expected,desc.html())

    def test_operator_not_implemented(self):
        kwargs=self.create_random_kwargs()
        obj=self.create_object(**kwargs)
        other=random.randint(1,10)
        
        with self.subTest(case="obj+num"):
            with self.assertRaises(TypeError) as cm:
                obj_sum=obj+other
        with self.subTest(case="num+obj"):
            with self.assertRaises(TypeError) as cm:
                obj_sum=other+obj
        with self.subTest(case="obj<num"):
            with self.assertRaises(TypeError) as cm:
                obj<other
        with self.subTest(case="num<obj"):
            with self.assertRaises(TypeError) as cm:
                other<obj
        with self.subTest(case="obj<=num"):
            with self.assertRaises(TypeError) as cm:
                obj<=other
        with self.subTest(case="num<=obj"):
            with self.assertRaises(TypeError) as cm:
                other<=obj
        
    def test_operator_cfr_disjointed(self): 
        kwargs1,kwargs2=self.create_two_kwargs_disjointed()
        obj1=self.create_object(**kwargs1)
        obj2=self.create_object(**kwargs2)
        with self.subTest(operator="=="): self.assertFalse(obj1==obj2)
        with self.subTest(operator="<"):  self.assertFalse(obj1<obj2)
        with self.subTest(operator="<="): self.assertFalse(obj1<=obj2)
        with self.subTest(operator=">"):  self.assertFalse(obj1>obj2)
        with self.subTest(operator=">="): self.assertFalse(obj1>=obj2)
        with self.subTest(operator="!="): self.assertTrue(obj1!=obj2)
        
    def test_operator_cfr_overlapping(self): 
        kwargs1,kwargs2=self.create_two_kwargs_overlapping()
        obj1=self.create_object(**kwargs1)
        obj2=self.create_object(**kwargs2)
        with self.subTest(operator="=="): self.assertFalse(obj1==obj2)
        with self.subTest(operator="<"):  self.assertFalse(obj1<obj2)
        with self.subTest(operator="<="): self.assertFalse(obj1<=obj2)
        with self.subTest(operator=">"):  self.assertFalse(obj1>obj2)
        with self.subTest(operator=">="): self.assertFalse(obj1>=obj2)
        with self.subTest(operator="!="): self.assertTrue(obj1!=obj2)

    def test_operator_cfr_incoherent(self): 
        kwargs1,kwargs2=self.create_two_kwargs_overlapping()
        obj1=self.create_object(**kwargs1)
        obj2=self.create_object(**kwargs2)
        with self.subTest(operator="=="): self.assertFalse(obj1==obj2)
        with self.subTest(operator="<"):  self.assertFalse(obj1<obj2)
        with self.subTest(operator="<="): self.assertFalse(obj1<=obj2)
        with self.subTest(operator=">"):  self.assertFalse(obj1>obj2)
        with self.subTest(operator=">="): self.assertFalse(obj1>=obj2)
        with self.subTest(operator="!="): self.assertTrue(obj1!=obj2)

    def test_operator_cfr_subset_first(self): 
        kwargs1,kwargs2=self.create_two_kwargs_subset_first()
        obj1=self.create_object(**kwargs1)
        obj2=self.create_object(**kwargs2)
        with self.subTest(operator="=="): self.assertFalse(obj1==obj2)
        with self.subTest(operator="<"):  self.assertTrue(obj1<obj2)
        with self.subTest(operator="<="): self.assertTrue(obj1<=obj2)
        with self.subTest(operator=">"):  self.assertFalse(obj1>obj2)
        with self.subTest(operator=">="): self.assertFalse(obj1>=obj2)
        with self.subTest(operator="!="): self.assertTrue(obj1!=obj2)

    def test_operator_cfr_subset_second(self): 
        kwargs1,kwargs2=self.create_two_kwargs_subset_second()
        obj1=self.create_object(**kwargs1)
        obj2=self.create_object(**kwargs2)
        with self.subTest(operator="=="): self.assertFalse(obj1==obj2)
        with self.subTest(operator="<"):  self.assertFalse(obj1<obj2)
        with self.subTest(operator="<="): self.assertFalse(obj1<=obj2)
        with self.subTest(operator=">"):  self.assertTrue(obj1>obj2)
        with self.subTest(operator=">="): self.assertTrue(obj1>=obj2)
        with self.subTest(operator="!="): self.assertTrue(obj1!=obj2)
        
    def test_operator_cfr_clone(self): 
        kwargs=self.create_random_kwargs()
        obj1=self.create_object(**kwargs)
        obj2=self.create_object(**kwargs)
        with self.subTest(operator="=="): self.assertTrue(obj1==obj2)
        with self.subTest(operator="<"):  self.assertFalse(obj1<obj2)
        with self.subTest(operator="<="): self.assertTrue(obj1<=obj2)
        with self.subTest(operator=">"):  self.assertFalse(obj1>obj2)
        with self.subTest(operator=">="): self.assertTrue(obj1>=obj2)
        with self.subTest(operator="!="): self.assertFalse(obj1!=obj2)
        
    def test_operator_plus_disjointed(self):
        kwargs1,kwargs2=self.create_two_kwargs_disjointed()
        obj1=self.create_object(**kwargs1)
        obj2=self.create_object(**kwargs2)
        obj_sum=obj1+obj2
        for k in kwargs1:
            with self.subTest(case="k in A",k=k):
                self.assertIn(k,obj_sum)
                self.assertEqual(kwargs1[k],obj_sum[k])
        for k in kwargs2:
            with self.subTest(case="k in B",k=k):
                self.assertIn(k,obj_sum)
                self.assertEqual(kwargs2[k],obj_sum[k])

    def test_operator_plus_overlapping(self):
        kwargs1,kwargs2=self.create_two_kwargs_overlapping()
        obj1=self.create_object(**kwargs1)
        obj2=self.create_object(**kwargs2)
        obj_sum=obj1+obj2
        for k in kwargs1:
            with self.subTest(case="k in A",k=k):
                self.assertIn(k,obj_sum)
                self.assertEqual(kwargs1[k],obj_sum[k])
        for k in kwargs2:
            with self.subTest(case="k in B",k=k):
                self.assertIn(k,obj_sum)
                self.assertEqual(kwargs2[k],obj_sum[k])

    def test_operator_plus_incoherent(self):
        kwargs1,kwargs2=self.create_two_kwargs_incoherent()
        obj1=self.create_object(**kwargs1)
        obj2=self.create_object(**kwargs2)
        with self.assertRaises(descriptions.FailedUnification) as cm:
            obj_sum=obj1+obj2




    
