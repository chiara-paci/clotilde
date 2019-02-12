# -*- coding: utf-8 -*-

from django.db import models
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save
from django.utils.functional import cached_property

import re

from . import tokens

# Create your models here.

# MARKERS=[ u"center",u"right",u"i",u"left"]
# NEW_LINES=[('RN',   '\r\n'),
#            ('NR',   '\n\r'),
#            ('N',    '\n'),
#            ('XB',   u'\x0b'),
#            ('XC',   u'\x0c'),
#            ('R',    '\r'),
#            ('X85',  u'\x85'),
#            ('X2028',chr(0x2028)),
#            ('X2029',chr(0x2029))]

# def replace_newline(S,repl,preserve=False):
#     if not preserve:
#         for (r,n) in NEW_LINES:
#             S=S.replace(n,repl)
#         return(S)
#     for (r,n) in NEW_LINES:
#         S=S.replace(n,r+repl)
#     return(S)


class AbstractName(models.Model):
    name = models.CharField(max_length=1024)

    class Meta:
        abstract = True

    def __str__(self): return(self.name)

    def clean(self):
        c=re.compile('.*:.*')
        if c.match(self.name):
            raise ValidationError("Names can not have colons")
        models.Model.clean(self)

class AbstractNameDesc(models.Model):
    name = models.CharField(max_length=1024)
    description = models.TextField(blank=True,default='')

    class Meta:
        abstract = True

    def __str__(self): return(self.name)

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

class TokenRegexpSetManager(models.Manager):
    def de_serialize(self,D):
        reg_set,created=self.get_or_create(name=D["name"])
        for rexp in D["regexps"]:
            t_rexp,created=TokenRegexp.objects.get_or_create(name=rexp["name"],regexp=rexp["regexp"])
            tr,created=TokenRegexpSetThrough.objects.get_or_create(token_regexp=t_rexp,token_regexp_set=reg_set,
                                                                   defaults={
                                                                       "bg_color": rexp["bg_color"],
                                                                       "fg_color": rexp["fg_color"],
                                                                       "order": rexp["order"],
                                                                       "disabled": rexp["disabled"],
                                                                   })
        return reg_set

class TokenRegexpSet(AbstractName):
    regexps = models.ManyToManyField(TokenRegexp,
                                     through='TokenRegexpSetThrough',blank=True)

    objects=TokenRegexpSetManager()

    def regexp_all(self):
        regs=[ r'\[/?'+x+r'\]' for x in tokens.MARKERS ]
        regs+=[ rexp_t for (name,label,bg,fg,rexp,rexp_t) in self.regexp_objects ]
        t="|".join(regs)
        t="("+t+")"
        return(t)

    def _f(self,t):
        for (name,label,bg,fg,rexp,rexp_t) in self.regexp_objects:
            print("==%s==" % t,[ord(x) for x in t])
            if rexp.match(t):
                return tokens.TokenBase(label,t)
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
        return self.regexp_objects,[ self._f(t) for t in tokens ]

    @cached_property
    def regexp_objects(self):
        objs=[]
        for rel in self.tokenregexpsetthrough_set.all():
            if rel.disabled: continue
            name=rel.token_regexp.name
            regexp=rel.token_regexp.regexp
            objs.append( (name,name.lower().replace(' ',''),
                          rel.bg_color,rel.fg_color,
                          re.compile('^'+regexp+'$'),regexp) )
        return(objs)

    def has_regexp(self,obj):
        return(self.tokenregexpsetthrough_set.filter(token_regexp=obj).exists())

    def serialize(self):
        return {
            "name": self.name,
            "regexps": [ r.serialize() for r in self.tokenregexpsetthrough_set.all() ]
        }


class TokenRegexpSetThrough(models.Model):
    token_regexp_set = models.ForeignKey(TokenRegexpSet,on_delete="cascade")
    token_regexp = models.ForeignKey(TokenRegexp,on_delete="cascade")
    bg_color = models.CharField(max_length=20,default="#ffff00")
    fg_color = models.CharField(max_length=20,default="#000000")
    order = models.IntegerField()
    disabled = models.BooleanField()

    class Meta:
        ordering = ['order','token_regexp_set']

    def __str__(self):
        if self.disabled: S="(D) "
        else: S=""
        S+=str(self.token_regexp_set)
        S+="/"+str(self.id)+":"
        S+=str(self.token_regexp)
        return(S)

    def regexp(self):
        return(self.token_regexp.regexp)

    def name(self):
        return(self.token_regexp.name)

    def serialize(self):
        return {
            "name": self.token_regexp.name,
            "regexp": self.token_regexp.regexp,
            "bg_color": self.bg_color,
            "fg_color": self.fg_color,
            "order": self.order,
            "disabled": self.disabled
        }

class AlphabeticOrderManager(models.Manager):
    def de_serialize(self,D):
        obj,created=self.get_or_create(name=D["name"],
                                       order=D["order"])
        return obj

ALPHA_ORDER="AaÁáÀàÄäÆæ:Bb:CcÇç;Dd;EeÈèÉéËë;Ff;Gg;Hh;Ii;Jj;Kk;Ll;Mm;OoÒòÓóÖöŒœ;Pp;Qq;Rr;SsŞş;Tt;UuÙùÚúÜü;Vv;Ww;Xx;Yy;Zz"
class AlphabeticOrder(AbstractName):
    order=models.CharField(max_length=2048,default=ALPHA_ORDER)

    objects=AlphabeticOrderManager()

    def serialize(self):
        return {
            "name": self.name,
            "order": self.order
        }

class Language(AbstractName):
    token_regexp_set = models.ForeignKey(TokenRegexpSet,on_delete="cascade")
    case_set = models.ForeignKey(CaseSet,default=1,on_delete="cascade")
    period_sep = models.ForeignKey(TokenRegexp,on_delete="cascade")
    alphabetic_order = models.ForeignKey(AlphabeticOrder,on_delete="cascade")

    def clean(self):
        if not self.token_regexp_set.has_regexp(self.period_sep):
            raise ValidationError('Period regexp must be in language token regexp set')
        models.Model.clean(self)

    def __unicode__(self): return(self.name)

    def has_case(self):
        return(self.case_set.length()!=0)

    def token_regexp_expression(self):
        return(self.token_regexp_set.regexp_all())


    def get_absolute_url(self):
        return( "/base/language/%d" % self.id )

    def part_of_speech_set(self):
        return(PartOfSpeech.objects.by_language(self))

    def derivation_set(self):
        return(Derivation.objects.by_language(self))

    def serialize(self):
        return { 
            "name": self.name,
            "alphabetic_order": self.alphabetic_order.serialize(),
            "token_regexp_set": self.token_regexp_set.serialize(),
            "case_set": self.case_set.serialize(),
            # questo dovrebbe essere solo un "link" a un oggetto in "token_regexp_set"
            "period_sep": self.period_sep.name
        }
        

class NotWord(AbstractName):
    language = models.ForeignKey('Language',on_delete="cascade")    
    word=models.CharField(max_length=1024,db_index=True)

    def __unicode__(self): return("not word: "+self.name)

def insert_newlines_as_notword(sender,instance,created,**kwargs):
    for (r,n) in tokens.NEW_LINES: 
        NotWord.objects.get_or_create(language=instance,name="new line ("+r+")",word=n)

post_save.connect(insert_newlines_as_notword,sender=Language)
