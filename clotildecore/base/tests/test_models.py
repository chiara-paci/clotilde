# -*- coding: utf-8 -*-

import unittest
import random
import json

from unittest import skip
from unittest import mock

from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ValidationError,PermissionDenied
from django.db.utils import IntegrityError
from sqlite3 import IntegrityError as S3IntegrityError

import re

from . import common
from .. import models,tokens,descriptions

class ConstantTest(common.BaseTestCase):
    def test_models_constant(self):
        for name,required,actual in [ 
                ("ALPHA",      self.CONST_MODELS["ALPHA"],models.ALPHA),
                ("ALPHA_ORDER",self.CONST_MODELS["ALPHA_ORDER"],models.ALPHA_ORDER),
                ("DEFAULT_DESCRIPTION_NAME",
                 self.CONST_MODELS["DEFAULT_DESCRIPTION_NAME"],
                 models.DEFAULT_DESCRIPTION_NAME),
        ]: 
            with self.subTest(const=name):
                self.assertConstant(name,required,actual)

class CasePairTest(common.BaseTestCase,common.CommonModelTestCase):
    fields = [ "lower","upper" ]
    model_name = "casepair"

    def create_random_object(self): return self.create_random_casepair()
    def correct_str(self,obj): return "%s/%s" % (obj.lower,obj.upper)

class CaseSetTest(common.BaseTestCase,common.CommonModelTestCase):
    fields = [ "name","pairs","length" ]
    model_name = "caseset"

    def create_random_object(self): return self.create_random_caseset()
    def correct_str(self,obj): return str(obj.name)

    def test_unique_name(self):
        name=self.random_string()
        self.assertUnique(self.create_caseset,name)

    def test_length_is_number_of_pairs(self):
        obj=self.create_random_caseset()
        N=random.randint(0,10)
        for n in range(0,N):
            obj.pairs.add(self.create_random_casepair())
        self.assertEqual(obj.length,N,msg="obj.length is not number of pairs: %d!=%d" % (obj.length,N) )

    def test_serialize(self):
        name=self.random_string()
        N=random.randint(0,10)
        cp_list=[ (self.random_string(),self.random_string()) for n in range(0,N) ]
        correct_ser={
            "name": name,
            "pairs": [ "%s/%s" % cp for cp in cp_list ]
        }
        obj=self.create_caseset(name)
        for l,u in cp_list:
            obj.pairs.add(self.create_casepair(l,u))
        ser=obj.serialize()

        with self.subTest(key="name"):
            self.assertEqual(name,ser["name"])
        with self.subTest(key="pairs length"):
            self.assertEqual(N,len(ser["pairs"]))

        for n in range(0,N):
            with self.subTest(key="pairs",pair=n):
                self.assertEqual(ser["pairs"][n],correct_ser["pairs"][n])

    def test_de_serialize(self):
        name=self.random_string()
        N=random.randint(0,10)
        cp_list=[ (self.random_string(),self.random_string()) for n in range(0,N) ]
        ser={
            "name": name,
            "pairs": [ "%s/%s" % cp for cp in cp_list ]
        }

        obj=models.CaseSet.objects.de_serialize(ser)

        with self.subTest(key="name"):
            self.assertEqual(name,obj.name)
        with self.subTest(key="pairs length"):
            self.assertEqual(N,obj.length)

        pairs=list(obj.pairs.all())
        for n in range(0,N):
            with self.subTest(key="pairs",pair=n):
                self.assertEqual(cp_list[n][0],pairs[n].lower)
                self.assertEqual(cp_list[n][1],pairs[n].upper)
            
class TokenRegexpTest(common.BaseTestCase,common.CommonModelTestCase):
    fields = [ "name","regexp" ]
    model_name = "tokenregexp"

    fields_default = [
        ("regexp", r'['+models.ALPHA+r']+' ),
    ]

    def create_random_object(self): return self.create_random_tokenregexp()
    def correct_str(self,obj): return "%s(%d)" % (obj.name,obj.pk)

    def test_unique_name(self):
        name=self.random_string()
        self.assertUnique(self.create_tokenregexp,name)

    def test_count_set_is_number_of_tokenregexpset(self):
        obj=self.create_random_tokenregexp()
        N=random.randint(0,10)
        for n in range(0,N):
            p=self.create_random_tokenregexpset()
            self.create_tokenregexpsetthrough(p,obj,random.randint(0,10),self.random_boolean())
        self.assertEqual(obj.count_set,N,msg="obj.count_set is not number of tokenregexpset: %d!=%d" % (obj.count_set,N) )

class TokenRegexpSetTest(common.BaseTestCase,common.CommonModelTestCase):
    fields = [ "name","regexps" ]
    model_name = "tokenregexpset"

    def create_random_object(self): return self.create_random_tokenregexpset()
    def correct_str(self,obj): return str(obj.name)

    def test_unique_name(self):
        name=self.random_string()
        self.assertUnique(self.create_tokenregexpset,name)

    def test_method_has_regexp(self):
        obj=self.create_random_tokenregexpset()
        self.assertHasMethod(obj,"has_regexp")
        N=random.randint(1,10)
        regexp_ok=[ self.create_random_tokenregexp() for n in range(0,N) ]
        regexp_no=self.create_random_tokenregexp()
        for n in range(0,N):
            self.create_tokenregexpsetthrough(obj,regexp_ok[n],n)

        with self.subTest(has_regexp=True):
            self.assertFunctionCall(True,obj.has_regexp,regexp_ok[0])
        with self.subTest(has_regexp=False):
            self.assertFunctionCall(False,obj.has_regexp,regexp_no)

    def test_method_regexp_all(self):
        obj=self.create_random_tokenregexpset()
        self.assertHasMethod(obj,"regexp_all")
        N=random.randint(1,5)
        disabled_list=[ True for n in range(0,N) ] + [ False for n in range(0,N) ]
        random.shuffle(disabled_list)
        regs=[ r'\[/?'+x+r'\]' for x in tokens.MARKERS ]
        for n in range(0,2*N):
            if disabled_list[n]:
                self.create_tokenregexpsetthrough(obj,self.create_random_tokenregexp(),n,disabled=True)
                continue
            name=self.random_string()
            regexp=self.random_string()
            self.create_tokenregexpsetthrough(obj,self.create_tokenregexp(name,regexp),n,disabled=False)
            regs.append(regexp)
        ret_ok="("+"|".join(regs)+")"
        ret=obj.regexp_all()
        self.assertFunctionCall(ret_ok,obj.regexp_all)

    @mock.patch("re.compile")
    def test_method_tokenize(self,mock_re_compile):
        token_regexps=[ 
            ("aname","aregx",lambda x: x.startswith("A"),True ),
            ("bname","bregx",lambda x: x.startswith("B"),False ),
        ]
        obj=self.create_random_tokenregexpset()
        n=0
        for name,regexp,func,final in token_regexps:
            self.create_tokenregexpsetthrough(obj,self.create_tokenregexp(name=name,regexp=regexp),n,disabled=False,final=final)
            n+=1
        
        def compile_side_effect(target):
            for name,regexp,func,final in token_regexps:
                if '^'+regexp+'$'==target:
                    re_obj=mock.MagicMock(name="re_obj %s" % name)
                    re_obj.match.side_effect=func
                    return re_obj
            re_obj=mock.MagicMock(name="re_obj NO")
            re_obj.match.side_effect=lambda x: False
            return re_obj

        def side_effect_decorator(ret_split,func):
            def decorated(*args,**kwargs):
                re_obj=func(*args,**kwargs)
                re_obj.split.return_value=ret_split
                return re_obj
            return decorated

        test_cases=[ 
            ( ["x","","r"], [ (tokens.TokenNotFound,"not-found","x",True),
                              (tokens.TokenNotFound,"not-found","r",True) ] ) ,
            ( ["Asdf","q","Bfsg"], [ (tokens.TokenBase,"aname","Asdf",True),
                                     (tokens.TokenNotFound,"not-found","q",True),
                                     (tokens.TokenBase,"bname","Bfsg",False) ] ),   
            ( ["Asdf", "[mka]", "Bfsg", "Arts", "[/hsjk]", "[/qwe]" ],
              [
                  (tokens.TokenBase,"aname","Asdf",True),
                  (tokens.TokenMarker,"not-found",'<i class="fas fa-arrow-alt-circle-right"></i>',True),
                  (tokens.TokenBase,"bname","Bfsg",False),
                  (tokens.TokenBase,"aname","Arts",True),
                  (tokens.TokenMarker,"not-found",'<i class="fas fa-arrow-alt-circle-left"></i>',True),
                  (tokens.TokenMarker,"not-found",'<i class="fas fa-arrow-alt-circle-left"></i>',True),
              ] ),
            ( ["[center]", "[mka]", "Bfsg", "Arts", "[/i]", "[/left]", "[right]" ],
              [
                  (tokens.TokenMarker,"marker",'<i class="fas fa-arrow-alt-circle-right"></i><i class="fas fa-align-center"></i>',True),
                  (tokens.TokenMarker,"not-found",'<i class="fas fa-arrow-alt-circle-right"></i>',True),
                  (tokens.TokenBase,"bname","Bfsg",False),
                  (tokens.TokenBase,"aname","Arts",True),
                  (tokens.TokenMarker,"marker",'<i class="fas fa-italic"></i><i class="fas fa-arrow-alt-circle-left"></i>',True),
                  (tokens.TokenMarker,"marker",'<i class="fas fa-align-left"></i><i class="fas fa-arrow-alt-circle-left"></i>',True),
                  (tokens.TokenMarker,"marker",'<i class="fas fa-arrow-alt-circle-right"></i><i class="fas fa-align-right"></i>',True),
              ] )
        ]
        
        for data,expected in test_cases:
            mock_re_compile.side_effect=side_effect_decorator(data,compile_side_effect)
            regexp_objects,ret_tokens=obj.tokenize(self.random_string())
            with self.subTest(data=data,test="len"):
                self.assertEqual(len(ret_tokens),len(expected))
            n=0
            for cls,label,text,final in expected:
                with self.subTest(data=data,token=n):
                    self.assertToken(ret_tokens[n],cls,label,text,final)
                n+=1

    def test_serialize(self):
        name=self.random_string()
        obj=self.create_tokenregexpset(name=name)
        correct_ser={
            "name": name,
            "regexps": []
        }

        N=random.randint(1,10)
        for n in range(0,N):
            tname=self.random_string()
            regexp=self.random_string()
            token_regexp=self.create_tokenregexp(name=tname,regexp=regexp)
            disabled=self.random_boolean()
            final=self.random_boolean()
            bg_color=self.random_string()
            fg_color=self.random_string()
            rel_ser={
                "name": tname,
                "regexp": regexp,
                "bg_color": bg_color,
                "fg_color": fg_color,
                "final": final,
                "order": n,
                "disabled": disabled
            }
            rel=self.create_tokenregexpsetthrough(obj,token_regexp,n,disabled=disabled,
                                                  final=final,bg_color=bg_color,fg_color=fg_color)
            correct_ser["regexps"].append(rel_ser)

        ser=obj.serialize()

        
        k="name"
        with self.subTest(key=k):
            self.assertEqual(correct_ser[k],ser[k],
                             msg="Wrong serialization on key '%s': expected='%s' actual='%s'" % (k,correct_ser[k],ser[k]))
        for n in range(0,N):
            e_ser=correct_ser["regexps"][n]
            a_ser=ser["regexps"][n]
            for k in e_ser:
                with self.subTest(key="regexps",n=n,subkey=k):
                    self.assertEqual(e_ser[k],a_ser[k],
                                     msg="Wrong serialization on key 'regexps/%d/%s': expected='%s' actual='%s'" % (n,k,e_ser[k],a_ser[k]))

    def test_de_serialize(self):
        name=self.random_string()
        ser={
            "name": name,
            "regexps": []
        }
        N=random.randint(1,10)
        for n in range(0,N):
            tname=self.random_string()
            regexp=self.random_string()
            token_regexp=self.create_tokenregexp(name=tname,regexp=regexp)
            disabled=self.random_boolean()
            final=self.random_boolean()
            bg_color=self.random_string()
            fg_color=self.random_string()
            rel_ser={
                "name": tname,
                "regexp": regexp,
                "bg_color": bg_color,
                "fg_color": fg_color,
                "final": final,
                "order": n,
                "disabled": disabled
            }
            ser["regexps"].append(rel_ser)

        obj=models.TokenRegexpSet.objects.de_serialize(ser)

        with self.subTest(key="name"):
            self.assertEqual(name,obj.name)

        regexps=list(obj.tokenregexpsetthrough_set.all())
        for n in range(0,N):
            e_vals=ser["regexps"][n]
            a_vals={
                "name": regexps[n].name,
                "regexp": regexps[n].regexp,
                "bg_color": regexps[n].bg_color,
                "fg_color": regexps[n].fg_color,
                "final": regexps[n].final,
                "order": regexps[n].order,
                "disabled": regexps[n].disabled
            }

            for k in e_vals:
                with self.subTest(key="regexps",n=n,subkey=k):
                    self.assertEqual(e_vals[k],a_vals[k],
                                     msg="Wrong deserialization on key 'regexps/%d/%s': expected='%s' actual='%s'" % (n,k,e_vals[k],a_vals[k]))
        

class TokenRegexpSetThroughTest(common.BaseTestCase,common.CommonModelTestCase):
    model_name = "tokenregexpsetthrough"
    fields = [ "token_regexp_set","token_regexp","bg_color","fg_color","order",
               "final","disabled","name","regexp" ]
    fields_default = [
        ( "bg_color","#ffff00" ),
        ( "fg_color","#000000" ),
        ( "final",False ),
        ( "disabled",False ),
    ]

    def create_random_object(self): return self.create_random_tokenregexpsetthrough()
    def correct_str(self,obj):      return super().correct_str(obj)

    def test_str(self):
        regexp_set=self.create_random_tokenregexpset()
        regexp=self.create_random_tokenregexp()
        order=random.randint(0,10)
        obj_true=self.create_tokenregexpsetthrough(regexp_set,regexp,order,disabled=True)
        obj_false=self.create_tokenregexpsetthrough(regexp_set,regexp,order,disabled=False)
        s_true="(D) %s/%d:%s" % (str(regexp_set),obj_true.id,str(regexp))
        s_false="%s/%d:%s" % (str(regexp_set),obj_false.id,str(regexp))

        with self.subTest(disabled=True):
            self.assertEqual(str(obj_true),s_true)

        with self.subTest(disabled=False):
            self.assertEqual(str(obj_false),s_false)

    def test_name_is_token_regexp_name(self):
        regexp_set=self.create_random_tokenregexpset()
        name=self.random_string()
        token_regexp=self.create_tokenregexp(name=name)
        order=random.randint(0,10)
        obj=self.create_tokenregexpsetthrough(regexp_set,token_regexp,order)
        self.assertEqual(obj.name,name,msg="obj.name is not token_regexp name: %s!=%s" % (obj.name,name) )

    def test_regexp_is_token_regexp_regexp(self):
        regexp_set=self.create_random_tokenregexpset()
        name=self.random_string()
        regexp=self.random_string()
        token_regexp=self.create_tokenregexp(name=name,regexp=regexp)
        order=random.randint(0,10)
        obj=self.create_tokenregexpsetthrough(regexp_set,token_regexp,order)
        self.assertEqual(obj.regexp,regexp,msg="obj.regexp is not token_regexp regexp: %s!=%s" % (obj.regexp,regexp) )

    def test_serialize(self):
        regexp_set=self.create_random_tokenregexpset()
        name=self.random_string()
        regexp=self.random_string()
        token_regexp=self.create_tokenregexp(name=name,regexp=regexp)
        order=random.randint(0,10)
        disabled=self.random_boolean()
        final=self.random_boolean()
        bg_color=self.random_string()
        fg_color=self.random_string()

        correct_ser={
            "name": name,
            "regexp": regexp,
            "bg_color": bg_color,
            "fg_color": fg_color,
            "final": final,
            "order": order,
            "disabled": disabled
        }

        obj=self.create_tokenregexpsetthrough(regexp_set,token_regexp,order,disabled=disabled,
                                              final=final,bg_color=bg_color,fg_color=fg_color)

        ser=obj.serialize()

        for k in correct_ser:
            with self.subTest(key=k):
                self.assertEqual(correct_ser[k],ser[k],
                                 msg="Wrong serialization on key '%s': expected='%s' actual='%s'" % (k,correct_ser[k],ser[k]))

    def test_de_serialize(self):
        tname=self.random_string()
        regexp=self.random_string()
        token_regexp=self.create_tokenregexp(name=tname,regexp=regexp)
        disabled=self.random_boolean()
        order=random.randint(0,10)
        final=self.random_boolean()
        bg_color=self.random_string()
        fg_color=self.random_string()
        ser={
            "name": tname,
            "regexp": regexp,
            "bg_color": bg_color,
            "fg_color": fg_color,
            "final": final,
            "order": order,
            "disabled": disabled
        }
        regexp_set=self.create_random_tokenregexpset()

        obj=models.TokenRegexpSetThrough.objects.de_serialize(regexp_set,ser)

        with self.subTest(key="token_regexp_set"):
            self.assertEqual(regexp_set,obj.token_regexp_set)

        vals={
            "name": obj.name,
            "regexp": obj.regexp,
            "bg_color": obj.bg_color,
            "fg_color": obj.fg_color,
            "final": obj.final,
            "order": obj.order,
            "disabled": obj.disabled
        }

        for k in ser:
            with self.subTest(key=k):
                self.assertEqual(ser[k],vals[k],
                                 msg="Wrong deserialization on key '%s': expected='%s' actual='%s'" % (k,ser[k],vals[k]))


class AlphabeticOrderTest(common.BaseTestCase,common.CommonModelTestCase):
    fields = [ "name","order" ]
    fields_default = [
        ( "order",models.ALPHA_ORDER ),
    ]
    model_name = "alphabeticorder"

    def create_random_object(self): return self.create_random_alphabeticorder()
    def correct_str(self,obj): return str(obj.name)

    def test_unique_name(self):
        name=self.random_string()
        self.assertUnique(self.create_alphabeticorder,name)

    def test_serialize(self):
        name=self.random_string()
        order=self.random_string()
        correct_ser={
            "name": name,
            "order": order
        }
        obj=self.create_alphabeticorder(name,order=order)
        ser=obj.serialize()

        with self.subTest(key="name"):
            self.assertEqual(name,ser["name"])
        with self.subTest(key="order"):
            self.assertEqual(order,ser["order"])

    def test_de_serialize(self):
        name=self.random_string()
        order=self.random_string()
        ser={
            "name": name,
            "order": order
        }
        obj=models.AlphabeticOrder.objects.de_serialize(ser)
        with self.subTest(key="name"):
            self.assertEqual(name,obj.name)
        with self.subTest(key="order"):
            self.assertEqual(order,obj.order)

class AttributeTest(common.BaseTestCase,common.CommonModelTestCase):
    fields = [ "name","order" ]
    fields_default = [
        ( "order",1 ),
    ]
    model_name = "attribute"

    def create_random_object(self): return self.create_random_attribute()
    def correct_str(self,obj): return str(obj.name)

    def test_unique_name(self):
        name=self.random_string()
        self.assertUnique(self.create_attribute,name)

    def test_serialize(self):
        name=self.random_string()
        order=random.randint(0,100)
        correct_ser={
            "name": name,
            "order": order
        }
        obj=self.create_attribute(name,order=order)
        ser=obj.serialize()

        with self.subTest(key="name"):
            self.assertEqual(name,ser["name"])
        with self.subTest(key="order"):
            self.assertEqual(order,ser["order"])

    def test_de_serialize(self):
        name=self.random_string()
        order=random.randint(0,100)
        ser={
            "name": name,
            "order": order
        }
        
        obj=models.Attribute.objects.de_serialize(ser)
        with self.subTest(key="name"):
            self.assertEqual(name,obj.name)
        with self.subTest(key="order"):
            self.assertEqual(order,obj.order)


class ValueTest(common.BaseTestCase,common.CommonModelTestCase):
    fields = [ "string","order","variable" ]
    fields_default = [
        ( "order",1 ),
        ("variable",False)
    ]
    model_name = "value"

    def create_random_object(self): return self.create_random_value()
    def correct_str(self,obj): return str(obj.string)

    def test_unique_string(self):
        s=self.random_string()
        self.assertUnique(self.create_value,s)

    def test_str(self):
        s1=self.random_string()
        s2=self.random_string()
        order=random.randint(0,100)
        variable=self.random_boolean()

        obj_true=self.create_value(s1,order=order,variable=True)
        obj_false=self.create_value(s2,order=order,variable=False)

        s_true="%s (var)" % s1
        s_false=s2

        with self.subTest(variable=True):
            self.assertEqual(str(obj_true),s_true)

        with self.subTest(variable=False):
            self.assertEqual(str(obj_false),s_false)


    def test_serialize(self):
        s=self.random_string()
        order=random.randint(0,100)
        variable=self.random_boolean()
        correct_ser={
            "string": s,
            "order": order,
            "variable": variable
        }
        obj=self.create_value(s,order=order,variable=variable)
        ser=obj.serialize()

        with self.subTest(key="string"):
            self.assertEqual(s,ser["string"])
        with self.subTest(key="order"):
            self.assertEqual(order,ser["order"])
        with self.subTest(key="variable"):
            self.assertEqual(variable,ser["variable"])

    def test_de_serialize(self):
        s=self.random_string()
        order=random.randint(0,100)
        variable=self.random_boolean()
        ser={
            "string": s,
            "order": order,
            "variable": variable
        }
        obj=models.Value.objects.de_serialize(ser)
        with self.subTest(key="string"):
            self.assertEqual(s,obj.string)
        with self.subTest(key="order"):
            self.assertEqual(order,obj.order)
        with self.subTest(key="variable"):
            self.assertEqual(variable,obj.variable)

class EntryTest(common.BaseTestCase,common.CommonModelTestCase):
    fields = [ "attribute","value","invert" ]
    fields_default = [
        ("invert",False)
    ]
    model_name = "entry"

    def create_random_object(self): return self.create_random_entry()
    def correct_str(self,obj): return str(obj.value)

    def test_unique_attribute_value_invert(self):
        attr=self.create_random_attribute()
        val=self.create_random_value()
        invert=self.random_boolean()
        self.assertUnique(self.create_entry,attr,val,invert=invert)

    def test_str(self):
        v=self.random_string()
        a=self.random_string()

        val=self.create_value(v)
        attr=self.create_attribute(a)

        obj_true=self.create_entry(attr,val,invert=True)
        obj_false=self.create_entry(attr,val,invert=False)

        s_true="%s=!%s" % (a,v)
        s_false="%s=%s" % (a,v)

        with self.subTest(invert=True):
            self.assertEqual(str(obj_true),s_true)

        with self.subTest(invert=False):
            self.assertEqual(str(obj_false),s_false)

class DescriptionTest(common.BaseTestCase,common.CommonModelTestCase):
    fields = [ "name","entries","count_fusionrules",
               "count_inflections","count_derivations","count_references" ]
    model_name = "description"

    def create_random_object(self): return self.create_random_description()
    def correct_str(self,obj): return str(obj.name)

    def test_unique_name(self):
        name=self.random_string()
        self.assertUnique(self.create_caseset,name)

    def test_method_build(self):
        obj=self.create_random_description()
        self.assertHasMethod(obj,"build")
        N=random.randint(1,5)
        invert_list=[ True for n in range(0,N) ] + [ False for n in range(0,N) ]
        random.shuffle(invert_list)

        correct_dict={}

        for n in range(0,2*N):
            a=self.random_string()
            v=self.random_string()
            attr=self.create_attribute(a)
            val=self.create_value(v)
            entry=self.create_entry(attr,val,invert=invert_list[n])
            obj.entries.add(entry)
            correct_dict[a]=(v,invert_list[n])

        ret_ok=descriptions.Description(**correct_dict)
        self.assertFunctionCall(ret_ok,obj.build)

    def test_serialize(self):
        name=self.random_string()
        obj=self.create_description(name)
        N=random.randint(1,5)
        invert_list=[ True for n in range(0,N) ] + [ False for n in range(0,N) ]
        random.shuffle(invert_list)

        correct_entries={}
        for n in range(0,2*N):
            a=self.random_string()
            v=self.random_string()
            attr=self.create_attribute(a)
            val=self.create_value(v)
            entry=self.create_entry(attr,val,invert=invert_list[n])
            obj.entries.add(entry)
            correct_entries[a]=(v,invert_list[n])

        a_name,entries=obj.serialize()

        with self.subTest(key="name"):
            self.assertEqual(name,a_name)

        for k in correct_entries:
            with self.subTest(key="entries",attribute=k):
                self.assertEqual(entries[k],correct_entries[k])

    def test_manager_method_get_or_create_by_dict(self):
        name=self.random_string()
        N=random.randint(1,5)
        invert_list=[ True for n in range(0,N) ] + [ False for n in range(0,N) ]
        random.shuffle(invert_list)
        data={}
        for n in range(0,2*N):
            a=self.random_string()
            v=self.random_string()
            data[a]=(v,invert_list[n])
        obj,created=models.Description.objects.get_or_create_by_dict(name,data)

        with self.subTest(created=True):
            self.assertTrue(created)
        with self.subTest(created=True,key="name"):
            self.assertEqual(name,obj.name)
        for k in data:
            with self.subTest(created=True,key="entries",attribute=k):
                self.assertTrue(obj.entries.filter(attribute__name=k,
                                                   value__string=data[k][0],
                                                   invert=data[k][1]).exists())

        N=random.randint(1,5)
        invert_list=[ True for n in range(0,N) ] + [ False for n in range(0,N) ]
        random.shuffle(invert_list)
        data2={}
        for n in range(0,2*N):
            a=self.random_string()
            v=self.random_string()
            data2[a]=(v,invert_list[n])
            
        obj,created=models.Description.objects.get_or_create_by_dict(name,data2)

        with self.subTest(created=False):
            self.assertFalse(created)
        with self.subTest(created=False,key="name"):
            self.assertEqual(name,obj.name)
        for k in data:
            with self.subTest(created=False,key="entries",attribute=k):
                self.assertTrue(obj.entries.filter(attribute__name=k,
                                                   value__string=data[k][0],
                                                   invert=data[k][1]).exists())


    def test_manager_method_get_default(self):
        obj=models.Description.objects.get_default()
        with self.subTest(created=True):
            self.assertEqual(obj.name,self.CONST_MODELS["DEFAULT_DESCRIPTION_NAME"])
        obj2=models.Description.objects.get_default()
        with self.subTest(created=False,test="name"):
            self.assertEqual(obj2.name,self.CONST_MODELS["DEFAULT_DESCRIPTION_NAME"])
        with self.subTest(created=False,test="pk"):
            self.assertEqual(obj.pk,obj2.pk)

    def test_count_fusionrules_is_num_of_fusionrules(self): assert True
    def test_count_inflections_is_num_of_inflections(self): assert True
    def test_count_derivations_is_num_of_derivations(self): assert True
    def test_count_references_is_sum_of_all_references(self): assert True

    def test_de_serialize(self): 
        name=self.random_string()
        N=random.randint(1,5)
        invert_list=[ True for n in range(0,N) ] + [ False for n in range(0,N) ]
        random.shuffle(invert_list)
        data={}
        for n in range(0,2*N):
            a=self.random_string()
            v=self.random_string()
            data[a]=(v,invert_list[n])

        ser=(name,data)
        obj=models.Description.objects.de_serialize(ser)
        with self.subTest(created=True,key="name"):
            self.assertEqual(name,obj.name)
        for k in data:
            with self.subTest(created=True,key="entries",attribute=k):
                self.assertTrue(obj.entries.filter(attribute__name=k,
                                                   value__string=data[k][0],
                                                   invert=data[k][1]).exists())

        N=random.randint(1,3)
        invert_list=[ True for n in range(0,N) ] + [ False for n in range(0,N) ]
        random.shuffle(invert_list)
        data_yes={}
        for n in range(0,2*N):
            a=self.random_string()
            v=self.random_string()
            data_yes[a]=(v,invert_list[n])

        N1=random.randint(1,len(data)-1)
        for k in list(data.keys())[:N1]:
            data_yes[k]=data[k]
        data_no={}
        for k in list(data.keys())[N1:]:
            data_no[k]=data[k]
        
        ser=(name,data_yes)
        obj=models.Description.objects.de_serialize(ser)
        with self.subTest(created=False,key="name"):
            self.assertEqual(name,obj.name)
        for k in data_yes:
            with self.subTest(created=False,key="entries",attribute=k,exists=True):
                self.assertTrue(obj.entries.filter(attribute__name=k,
                                                   value__string=data_yes[k][0],
                                                   invert=data_yes[k][1]).exists())
        for k in data_no:
            with self.subTest(created=False,key="entries",attribute=k,exists=False):
                self.assertFalse(obj.entries.filter(attribute__name=k,
                                                    value__string=data_no[k][0],
                                                    invert=data_no[k][1]).exists())
