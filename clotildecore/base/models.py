# -*- coding: utf-8 -*-

from django.db import models
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save
from django.utils.functional import cached_property

import re

from . import tokens

# Create your models here.

MARKERS=[ u"center",u"right",u"i",u"left"]
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

class CaseSet(AbstractName):
    pairs = models.ManyToManyField(CasePair,blank=True)

    def length(self):
        return(self.pairs.count())

    def get_absolute_url(self):
        return("/base/caseset/%d" % self.id)

ALPHA=u'a-zA-ZàèìòùáéíóúÀÈÌÒÙÁÉÍÓÚ'
class TokenRegexp(AbstractName):
    regexp = models.CharField(max_length=2048,default=r'['+ALPHA+r']+')

class TokenRegexpSet(AbstractName):
    regexps = models.ManyToManyField(TokenRegexp,through='TokenRegexpSetThrough',blank=True)

    def regexp_all(self):
        regs=[ r'\[/?'+x+r'\]' for x in MARKERS ]
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

ALPHA_ORDER="AaÁáÀàÄäÆæ:Bb:CcÇç;Dd;EeÈèÉéËë;Ff;Gg;Hh;Ii;Jj;Kk;Ll;Mm;OoÒòÓóÖöŒœ;Pp;Qq;Rr;SsŞş;Tt;UuÙùÚúÜü;Vv;Ww;Xx;Yy;Zz"
class AlphabeticOrder(AbstractName):
    order=models.CharField(max_length=2048,default=ALPHA_ORDER)

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

class NotWord(AbstractName):
    language = models.ForeignKey('Language',on_delete="cascade")    
    word=models.CharField(max_length=1024,db_index=True)

    def __unicode__(self): return("not word: "+self.name)

def insert_newlines_as_notword(sender,instance,created,**kwargs):
    for (r,n) in tokens.NEW_LINES: 
        NotWord.objects.get_or_create(language=instance,name="new line ("+r+")",word=n)

post_save.connect(insert_newlines_as_notword,sender=Language)
