# -*- coding: utf-8 -*-

from django.db import models
from django.core.exceptions import ValidationError

import re

# Create your models here.

ALPHA=u'a-zA-ZàèìòùáéíóúÀÈÌÒÙÁÉÍÓÚ'
MARKERS=[u"center",u"right",u"i",u"left"]
ALPHA_ORDER="AaÁáÀàÄäÆæ:Bb:CcÇç;Dd;EeÈèÉéËë;Ff;Gg;Hh;Ii;Jj;Kk;Ll;Mm;OoÒòÓóÖöŒœ;Pp;Qq;Rr;SsŞş;Tt;UuÙùÚúÜü;Vv;Ww;Xx;Yy;Zz"
NEW_LINES=[('RN',   '\r\n'),
           ('NR',   '\n\r'),
           ('N',    '\n'),
           ('XB',   u'\x0b'),
           ('XC',   u'\x0c'),
           ('R',    '\r'),
           ('X85',  u'\x85'),
           ('X2028',unichr(0x2028)),
           ('X2029',unichr(0x2029))]

class AbstractName(models.Model):
    name = models.CharField(max_length=1024)

    class Meta:
        abstract = True

    def __unicode__(self): return(self.name)

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

    def __unicode__(self): return(self.name)

class CasePair(models.Model):
    lower = models.CharField(max_length=10)
    upper = models.CharField(max_length=10)

    def __unicode__(self):
        return(self.lower+"/"+self.upper)

    def get_absolute_url(self):
        return("/base/casepair/%d" % self.id)

class CaseSet(AbstractName):
    pairs = models.ManyToManyField(CasePair,blank=True)

    def length(self):
        return(self.pairs.count())

    def get_absolute_url(self):
        return("/base/caseset/%d" % self.id)

class TokenRegexp(AbstractName):
    regexp = models.CharField(max_length=2048,default=r'['+ALPHA+r']+')

class TokenRegexpSet(AbstractName):
    regexps = models.ManyToManyField(TokenRegexp,through='TokenRegexpSetThrough',blank=True)

    def regexp_all(self):
        regs=map(lambda x: r'\[/?'+x+r'\]',MARKERS)
        for rel in self.tokenregexpsetthrough_set.all():
            if rel.disabled: continue
            regs.append(rel.regexp())
        t="|".join(regs)
        t="("+t+")"
        return(t)

    def regexp_objects(self):
        objs=[]
        for rel in self.tokenregexpsetthrough_set.all():
            if rel.disabled: continue
            name=rel.token_regexp.name
            objs.append( (name,name.lower().replace(' ',''),
                          rel.bg_color,rel.fg_color,re.compile('^'+rel.regexp()+'$'),rel.regexp()) )
        return(objs)

    def has_regexp(self,obj):
        return(self.tokenregexpsetthrough_set.filter(token_regexp=obj).exists())

class TokenRegexpSetThrough(models.Model):
    token_regexp_set = models.ForeignKey(TokenRegexpSet)
    token_regexp = models.ForeignKey(TokenRegexp)
    bg_color = models.CharField(max_length=20,default="#ffff00")
    fg_color = models.CharField(max_length=20,default="#000000")
    order = models.IntegerField()
    disabled = models.BooleanField()

    class Meta:
        ordering = ['order','token_regexp_set']

    def __unicode__(self):
        if self.disabled: S="(D) "
        else: S=""
        S+=unicode(self.token_regexp_set)
        S+="/"+unicode(self.id)+":"
        S+=unicode(self.token_regexp)
        return(S)

    def regexp(self):
        return(self.token_regexp.regexp)

    def name(self):
        return(self.token_regexp.name)

class AlphabeticOrder(AbstractName):
    order=models.CharField(max_length=2048,default=ALPHA_ORDER)

