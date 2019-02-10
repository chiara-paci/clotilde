#! /usr/bin/python
# -*- coding: utf-8 -*-

import re,time

from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist
#from morphology.models import *
#from languages.models import *
#from base.models import *

from base import models

##### language

def get_or_create_language(comp):
    k='case_set'
    caseset_pairs_def=[]
    for v in comp[k]:
        t=v.split(":")
        if t[1]=="basedata":
            caseset_name=t[2]
            continue
        caseset_pairs_def.append( (t[2],t[3]) )

    k='tokenregexpset'
    tokenregexpset_regexps_def=[]
    for v in comp[k]:
        t=v.split(":")
        if t[1]=="basedata":
            tokenregexpset_name=t[2]
            continue
        # tokenregexpset:1:tokenregexp:4:space:0:2:#c0ffc0:#000000:[ ]
        #                              2:3    :4:5:6      :7      :8-
        l=t[2:8]
        l.append(':'.join(t[8:]))
        tokenregexpset_regexps_def.append(l)

    k='language'
    langpar={}
    for v in comp[k]:
        t=v.split(':')
        if t[0]!="alphabetic_order":
            langpar[t[0]]=t[1]
            continue
        (ao_id,ao_name)=t[2:4]
        ao_order=':'.join(t[4:])

    def casepairs_add(cset,pairs_def):
        for (lower,upper) in pairs_def:
            cpair,created=models.CasePair.objects.get_or_create(lower=lower,upper=upper)
            if created: print("Create %s: %s,%s" % ("case pair",lower,upper))
            if not cset.pairs.filter(id=cpair.id).exists():
                cset.pairs.add(cpair)

    def tokenregexps_add(tset,regs_def,period_id=None):
        ret=None
        for (tid,tname,tdisabled,torder,tfg,tbg,tregexp) in regs_def:
            torder=int(torder)
            tdisabled=(tdisabled=='1')
            tr,created=models.TokenRegexp.objects.get_or_create(name=tname,regexp=tregexp)
            if created:    
                print("Create %s: %s,%s" % ("token regexp",tname,tregexp))

            trst,created=models.TokenRegexpSetThrough.objects.get_or_create(token_regexp=tr,token_regexp_set=tset,
                                                                            defaults={"bg_color":tbg,"fg_color":tfg,
                                                                                      "order":torder,"disabled":tdisabled})
            if created:
                print("Create %s: %s/%d:%s" % ("token regexp set through",tset.name,torder,tname))
                                                          
            if period_id and tid==period_id: 
                ret=tr
        return(ret)
    
    try:
        language=models.Language.objects.get(name=langpar["name"])
        tokenregexpset=language.token_regexp_set
        caseset=language.case_set
        casepairs_add(caseset,caseset_pairs_def)
        tokenregexps_add(tokenregexpset,tokenregexpset_regexps_def)
    except models.Language.DoesNotExist as e:
        caseset,created=models.CaseSet.objects.get_or_create(name=caseset_name)
        if created: print("Create %s: %s" % ("caseset",str(caseset)))
        tokenregexpset,created=models.TokenRegexpSet.objects.get_or_create(name=tokenregexpset_name)
        if created: print("Create %s: %s" % ("tokenregexpset",str(tokenregexpset)))
        casepairs_add(caseset,caseset_pairs_def)
        period_sep=tokenregexps_add(tokenregexpset,tokenregexpset_regexps_def,period_id=langpar["period_sep"])
        ao,created=models.AlphabeticOrder.objects.get_or_create(name=ao_name,order=ao_order)
        if created:
            print("Create %s: %s" % ("alphabetic order",ao_name))
        language=models.Language.objects.create(name=langpar["name"],token_regexp_set=tokenregexpset,case_set=caseset,
                                                period_sep=period_sep,alphabetic_order=ao)
    return(language)



class Command(BaseCommand):
    requires_migrations_checks = True
    help = 'Export <language>'

    def add_arguments(self, parser):
        parser.add_argument(
            'language',
            help='Language file',
        )

    def handle(self, *args, **options):
        fname = options["language"]
        #fname=args[0]
        fd=open(fname,'r')
        text=fd.read()
        #text=str(text)
        fd.close()
        
        lines=text.split('\n')

        comp={}

        for l in lines:
            if not l: continue
            if l[0]=='#': continue
            t=l.split(':')
            k=t[0]
            v=':'.join(t[1:])
            if not k in comp: comp[k]=[]
            comp[k].append(v)

        language=get_or_create_language(comp)

        #impobjs=ImportObjects(language,comp)




