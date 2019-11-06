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
    def create_random_object(self): return None

    @abc.abstractmethod
    def create_object(self,*args,**kwargs):
        return None

    @abc.abstractmethod
    def make_parameters(self,*args,**kwargs):
        label=""
        text=""
        desc=None
        final=None # boolean
        return label,text,desc,final

    def test_object_has_attributes(self):
        obj=self.create_random_object()
        for a in self.attributes:
            with self.subTest(attribute=a):
                self.assertHasAttribute(obj,a)

    def _test_method_html(self,*args,**kwargs):
        obj=self.create_object(*args,**kwargs)
        label,text,desc,final=self.make_parameters(*args,**kwargs)
        exp_format='<span class="token %s">%s</span>'
        expected=exp_format % ( label, text.replace("¶","¶<br/>"))
        result=obj.html()
        self.assertTrue(expected,result)

    def _test_attribute_values(self,*args,**kwargs):
        obj=self.create_object(*args,**kwargs)
        label,text,desc,final=self.make_parameters(*args,**kwargs)
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
        label,text,desc,final=self.make_parameters(*args,**kwargs)
        expected=hash(label+":"+text+"/"+str(desc))
        self.assertFunctionCall(expected,hash,obj)

    def _test_object_is_sortable(self,param_list):
        random.shuffle(param_list)
        obj_list=[]
        expected_list=[]
        for args,kwargs in param_list:
            obj=self.create_object(*args,**kwargs)
            label,text,desc,final=self.make_parameters(*args,**kwargs)
            expected_list.append( (text.lower(),desc,obj) )
            obj_list.append(obj)
        obj_list.sort()
        expected_list.sort()

        for n in range(0,len(obj_list)):
            with self.subTest(n=n):
                msg="expected: %s %s, actual: %s %s" % (expected_list[n][0],str(expected_list[n][1]),
                                                        obj.text,str(obj.description)) 
                self.assertEqual(obj_list[n],expected_list[n][2],msg=msg)




    
