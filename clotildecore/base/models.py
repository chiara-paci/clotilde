# -*- coding: utf-8 -*-

from django.db import models
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save
from django.utils.functional import cached_property
from django.conf import settings

import re

from . import tokens,descriptions,functions

class AbstractName(models.Model):
    name = models.CharField(max_length=1024,unique=True)

    class Meta:
        abstract = True
        ordering = [ "name" ]

    def __str__(self): return(self.name)

    def clean(self):
        c=re.compile('.*:.*')
        if c.match(self.name):
            raise ValidationError("Names can not have colons")
        models.Model.clean(self)

class AbstractNameDesc(models.Model):
    name = models.CharField(max_length=1024,unique=True)
    description = models.TextField(blank=True,default='')

    class Meta:
        abstract = True

    def __str__(self): return(self.name)

######

class CasePair(models.Model):
    lower = models.CharField(max_length=10)
    upper = models.CharField(max_length=10)

    def __str__(self):
        return(self.lower+"/"+self.upper)

    def get_absolute_url(self):
        return("/base/casepair/%d" % self.id)

class CaseSetManager(models.Manager):
    def de_serialize(self,D):
        case_set,created=self.get_or_create(name=D["name"])
        for pair in D["pairs"]:
            p=pair.split("/")
            case_pair,created=CasePair.objects.get_or_create(lower=p[0],upper=p[1])
            case_set.pairs.add(case_pair)
        return case_set

class CaseSet(AbstractName):
    pairs = models.ManyToManyField(CasePair,blank=True)

    objects = CaseSetManager()

    @cached_property
    def length(self):
        return(self.pairs.count())

    def get_absolute_url(self):
        return("/base/caseset/%d" % self.id)

    def serialize(self):
        return {
            "name": self.name,
            "pairs": [ str(cp) for cp in self.pairs.all() ]
        }

ALPHA=u'a-zA-ZàèìòùáéíóúÀÈÌÒÙÁÉÍÓÚ'
class TokenRegexp(AbstractName):
    regexp = models.CharField(max_length=2048,default=r'['+ALPHA+r']+')

    def __str__(self):
        return "%s(%d)" % (self.name,self.pk)

    def get_absolute_url(self):
        return("/base/tokenregexp/%d" % self.id)

    @cached_property
    def count_set(self):
        return self.tokenregexpsetthrough_set.all().count()

class TokenRegexpSetManager(models.Manager):
    def de_serialize(self,D):
        reg_set,created=self.get_or_create(name=D["name"])
        for rexp in D["regexps"]:
            tr=TokenRegexpSetThrough.objects.de_serialize(reg_set,rexp)
        return reg_set

class TokenRegexpSet(AbstractName):
    regexps = models.ManyToManyField(TokenRegexp,
                                     through='TokenRegexpSetThrough',blank=True)

    objects=TokenRegexpSetManager()

    def get_absolute_url(self):
        return("/base/tokenregexpset/%d" % self.id)

    def _regexp_objects(self):
        objs=[]
        for rel in self.tokenregexpsetthrough_set.all():
            if rel.disabled: continue
            name=rel.token_regexp.name
            regexp=rel.token_regexp.regexp
            objs.append( (name,name.lower().replace(' ',''),
                          rel.bg_color,rel.fg_color,rel.final,
                          re.compile('^'+regexp+'$'),regexp) )
        return(objs)

    def _f(self,t,regexp_objects):
        for (name,label,bg,fg,final,rexp,rexp_t) in regexp_objects:
            if rexp.match(t):
                return tokens.TokenBase(label,t,final=final)
        if t[0]=='[':
            if t[1]=="/":
                m=t[2:-1]
                return tokens.TokenMarker(m,"end")
            m=t[1:-1]
            return tokens.TokenMarker(m,"begin")
        return tokens.TokenNotFound(t)

    def tokenize(self,text):
        c=re.compile(self.regexp_all())
        tokens=list(filter(bool,c.split(text)))
        regexp_objects=self._regexp_objects()
        return regexp_objects,[ self._f(t,regexp_objects) for t in tokens ]

    def regexp_all(self):
        regs=[ r'\[/?'+x+r'\]' for x in tokens.MARKERS ]
        regs+=[ rel["token_regexp__regexp"] for rel in self.tokenregexpsetthrough_set.filter(disabled=False).values("token_regexp__regexp") ]
        t="|".join(regs)
        t="("+t+")"
        return(t)

    def has_regexp(self,obj):
        return(self.tokenregexpsetthrough_set.filter(token_regexp=obj).exists())

    def serialize(self):
        return {
            "name": self.name,
            "regexps": [ r.serialize() for r in self.tokenregexpsetthrough_set.all() ]
        }

class TokenRegexpSetThroughManager(models.Manager):
    def de_serialize(self,token_set,ser): 
        t_rexp,created=TokenRegexp.objects.get_or_create(name=ser["name"],regexp=ser["regexp"])
        obj,created=TokenRegexpSetThrough.objects.update_or_create(token_regexp=t_rexp,
                                                                   token_regexp_set=token_set,
                                                                   defaults={
                                                                      "bg_color": ser["bg_color"],
                                                                      "fg_color": ser["fg_color"],
                                                                      "order":    ser["order"],
                                                                      "final":    ser["final"],
                                                                      "disabled": ser["disabled"],
                                                                  })
        return obj

class TokenRegexpSetThrough(models.Model):
    token_regexp_set = models.ForeignKey(TokenRegexpSet,on_delete="cascade")
    token_regexp = models.ForeignKey(TokenRegexp,on_delete="cascade")
    order = models.IntegerField()
    bg_color = models.CharField(max_length=20,default="#ffff00")
    fg_color = models.CharField(max_length=20,default="#000000")
    final = models.BooleanField(default=False)
    disabled = models.BooleanField(default=False)

    objects=TokenRegexpSetThroughManager()

    class Meta:
        ordering = ['order','token_regexp_set']

    def get_absolute_url(self):
        return("/base/tokenregexpsetthrough/%d" % self.id)

    def __str__(self):
        if self.disabled: S="(D) "
        else: S=""
        S+=str(self.token_regexp_set)
        S+="/"+str(self.id)+":"
        S+=str(self.token_regexp)
        return(S)

    @cached_property
    def regexp(self):
        return(self.token_regexp.regexp)

    @cached_property
    def name(self):
        return(self.token_regexp.name)

    def serialize(self):
        return {
            "name": self.token_regexp.name,
            "regexp": self.token_regexp.regexp,
            "bg_color": self.bg_color,
            "fg_color": self.fg_color,
            "final": self.final,
            "order": self.order,
            "disabled": self.disabled
        }

class AlphabeticOrderManager(models.Manager):
    def de_serialize(self,D):
        obj,created=self.update_or_create(name=D["name"],
                                          defaults={"order":D["order"]})
        obj.order=D["order"]
        obj.save()
        return obj

ALPHA_ORDER="AaÁáÀàÄäÆæ;Bb;CcÇç;Dd;EeÈèÉéËë;Ff;Gg;Hh;Ii;Jj;Kk;Ll;Mm;OoÒòÓóÖöŒœ;Pp;Qq;Rr;SsŞş;Tt;UuÙùÚúÜü;Vv;Ww;Xx;Yy;Zz"
class AlphabeticOrder(AbstractName):
    order=models.CharField(max_length=2048,default=ALPHA_ORDER)

    objects=AlphabeticOrderManager()

    def serialize(self):
        return {
            "name": self.name,
            "order": self.order
        }

    def get_absolute_url(self):
        return("/base/alphabeticorder/%d" % self.id)

class AttributeManager(models.Manager):
    def de_serialize(self,ser):
        defaults={
            "order": ser["order"]
        }
        obj,created=self.update_or_create(name=ser["name"],defaults=defaults)
        return obj

class Attribute(AbstractName): 
    order = models.IntegerField(default=1)
    objects=AttributeManager()

    def get_absolute_url(self):
        return("/base/attribute/%d" % self.id)

    def serialize(self):
        return {
            "name": self.name,
            "order": self.order
        }

    class Meta:
        ordering = ["order"]

class ValueManager(models.Manager):
    def de_serialize(self,ser):
        defaults={
            "order": ser["order"],
            "variable": ser["variable"]
        }
        obj,created=self.update_or_create(string=ser["string"],defaults=defaults)
        return obj

class Value(models.Model):
    string=models.CharField(max_length=1024,db_index=True,unique=True)
    variable = models.BooleanField(default=False)
    order = models.IntegerField(default=1)
    objects=ValueManager()

    def get_absolute_url(self):
        return("/base/value/%d" % self.id)

    def serialize(self):
        return {
            "string": self.string,
            "order": self.order,
            "variable": self.variable
        }

    class Meta:
        ordering = ["order"]

    def __str__(self):
        S=self.string
        if self.variable:
            S+=" (var)"
        return S
    
class Entry(models.Model):
    attribute = models.ForeignKey(Attribute,on_delete="protect")    
    value = models.ForeignKey(Value,on_delete="protect")    
    invert = models.BooleanField(default=False)

    def __str__(self):
        v=str(self.value)
        if self.invert:
            v="!"+v
        return "%s=%s" % (self.attribute,v)

    def get_absolute_url(self):
        return("/base/entry/%d" % self.id)

    class Meta:
        ordering = [ "attribute","value" ]
        unique_together = [ ["attribute","value","invert"] ]

DEFAULT_DESCRIPTION_NAME="vuota"

class DescriptionManager(models.Manager):

    def get_default(self):
        desc,created=self.get_or_create(name=DEFAULT_DESCRIPTION_NAME)
        return desc

    def _create_entry(self,key,edata): 
        attr,created=Attribute.objects.get_or_create(name=key)

        if type(edata) is tuple:
            value,created=Value.objects.get_or_create(string=edata[0])
            entry,created=Entry.objects.get_or_create(attribute=attr,value=value,invert=edata[1])
            return [entry] #,[]

        value,created=Value.objects.get_or_create(string=edata)
        entry,created=Entry.objects.get_or_create(attribute=attr,value=value) #,invert=False)
        return [entry] #,[]

    def get_or_create_by_dict(self,name,data):
        obj,created=self.get_or_create(name=name)
        if not created: return obj,False

        for k in data:
            entries=self._create_entry(k,data[k])
            for e in entries: obj.entries.add(e)

        return obj,True

    def de_serialize(self,ser):
        name,data=ser
        obj,created=self.get_or_create(name=name)
        e_ok=[]
        for k in data:
            attr,created=Attribute.objects.get_or_create(name=k)
            value,created=Value.objects.get_or_create(string=data[k][0])
            entry,created=Entry.objects.get_or_create(attribute=attr,value=value,invert=data[k][1])
            obj.entries.add(entry)
            e_ok.append(entry.pk)
        obj.entries.remove( *obj.entries.exclude(pk__in=e_ok) )
        return obj
    
class Description(AbstractName): 
    entries = models.ManyToManyField(Entry,blank=True)

    objects = DescriptionManager()

    class Meta:
        ordering = [ "name" ]

    def get_absolute_url(self):
        return("/base/description/%d" % self.id)

    def build(self):
        args=[ (str(e.attribute), ( str(e.value),e.invert) ) for e in self.entries.all() ]
        kwargs=dict(args)
        return descriptions.Description(**kwargs)

    def serialize(self):
        kwargs=[ ( str(e.attribute), ( str(e.value), e.invert ) ) for e in self.entries.all() ]
        # kwargsb=[ e.serialize() for e in self.subdescriptions.all() ]
        return (self.name,dict(kwargs)) #+kwargsb))

    @cached_property
    def count_fusionrules(self): return self.fusionrule_set.count()

    @cached_property
    def count_inflections(self): return self.inflection_set.count()

    @cached_property
    def count_derivations(self): return self.derivation_set.count()

    @cached_property
    def count_references(self): 
        N=0
        N+=self.count_fusionrules
        N+=self.count_inflections
        N+=self.count_derivations
        return N
    
