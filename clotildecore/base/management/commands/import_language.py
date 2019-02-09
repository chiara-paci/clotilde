#! /usr/bin/python
# -*- coding: utf-8 -*-

import re,time

from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist,MultipleObjectsReturned
from django.db.models import Q
from morphology.models import *
from languages.models import *

class ImportObjects(object):
    def __init__(self,language,comp):
        self.language=language
        self.comp=comp
        self.mk_functions={ 
            "category": self.mk_category,
            "partofspeech": self.mk_partofspeech,
            "regexpreplacement": self.mk_regexpreplacement,
            "classification": self.mk_classification,
            "paradigma": self.mk_paradigma,
            "capitalizedword": self.mk_capitalizedword,
            "morphologicalrule": self.mk_morphologicalrule,
            "derivation": self.mk_derivation,
            "root": self.mk_root
            }
        self.category=self.mk_objects("category")
        self.partofspeech=self.mk_objects("partofspeech")
        self.regexpreplacement=self.mk_objects("regexpreplacement")
        self.classification=self.mk_objects("classification")
        self.capitalizedword=self.mk_objects("capitalizedword")
        self.objclass={
            "morphologicalrule": self.sum_classifications("morphologicalrule"),
            "root_derivation": self.sum_classifications("derivation",pref="root_"),
            "dst_derivation": self.sum_classifications("derivation",pref="dst_"),
            "root": self.sum_classifications("root"),
            }        
        self.morphologicalrule=self.mk_objects("morphologicalrule")

        k="paradigma"
        ret={}
        for c in self.comp[k]:
            v=c.split(':')
            if v[1]!="morphologicalrule": continue
            vid=v[0]
            cid=v[2]
            if not ret.has_key(vid):
                ret[vid]=[]
            ret[vid].append(self.morphologicalrule[cid])
        self.parmr=ret
        self.paradigma=self.mk_objects("paradigma")

        self.derivation=self.mk_objects("derivation")
        self.root=self.mk_objects("root")

    def sum_classifications(self,k,pref=''):
        l=pref+"classification"
        ret={}
        for c in self.comp[k]:
            v=c.split(':')
            if v[1]!=l: continue
            vid=v[0]
            cid=v[2]
            negate=(v[3]=="1")
            if not ret.has_key(vid):
                ret[vid]=[]
            ret[vid].append( (self.classification[cid],negate) )
        return(ret)

    def mk_derivation(self,v,vid):
        if v[0]!='AAA': return None,False
        par=self.paradigma[v[1]]
        reg=self.regexpreplacement[v[2]]
        prod=(v[3]=="1")
        root_pos=self.partofspeech[v[4]]
        dst_pos=self.partofspeech[v[5]]
        name=v[6]
        try:
            if self.objclass["root_derivation"].has_key(vid):
                rcls=self.objclass["root_derivation"][vid]
            else:
                rcls=[]
            if self.objclass["dst_derivation"].has_key(vid):
                dcls=self.objclass["dst_derivation"][vid]
            else:
                dcls=[]
            qset=Derivation.objects.filter_root_dst_classifications(rcls,dcls)
            obj=qset.get(regexp=reg,paradigma=par,root_part_of_speech=root_pos,dst_part_of_speech=dst_pos)
            flag=False
        except MultipleObjectsReturned, e:
            try:
                obj=qset.filter(regexp=reg,paradigma=par,root_part_of_speech=root_pos,dst_part_of_speech=dst_pos).get(name=name,productive=prod)
                flag=False
            except ObjectDoesNotExist, e:
                obj=Derivation.objects.create(regexp=reg,paradigma=par,root_part_of_speech=root_pos,dst_part_of_speech=dst_pos,
                                              name=name,productive=prod)
                flag=True
        except ObjectDoesNotExist, e:
            obj=Derivation.objects.create(regexp=reg,paradigma=par,root_part_of_speech=root_pos,dst_part_of_speech=dst_pos,
                                          name=name,productive=prod)
            flag=True
        if flag:
            if self.objclass["root_derivation"].has_key(vid):
                for (cls,negate) in self.objclass["root_derivation"][vid]:
                    tobj,created=DerivationRootClassification.objects.get_or_create(derivation=obj,classification=cls,negate=negate)
                    if created:
                        print "Create rel. %s" % (unicode(tobj))
            if self.objclass["dst_derivation"].has_key(vid):
                for (cls,negate) in self.objclass["dst_derivation"][vid]:
                    tobj,created=DerivationDstClassification.objects.get_or_create(derivation=obj,classification=cls,negate=negate)
                    if created:
                        print "Create rel. %s" % (unicode(tobj))
        return obj,flag

    def mk_root(self,v,vid):
        if v[0]!='AAA': return None,False
        pos=self.partofspeech[v[1]]
        root=v[2]
        verbose=v[3]
        try:
            if self.objclass["root"].has_key(vid):
                cls=self.objclass["root"][vid]
            else:
                cls=[]
            qset=Root.objects.filter_classifications(cls)
            obj=qset.get(language=self.language,root=root,part_of_speech=pos,verbose=verbose)
            flag=False
        except ObjectDoesNotExist, e:
            obj=Root.objects.create(language=self.language,root=root,part_of_speech=pos,verbose=verbose)
            flag=True
        if flag:
            for (cls,negate) in self.objclass["root"][vid]:
                tobj,created=RootClassification.objects.get_or_create(root=obj,classification=cls,negate=negate)
                if created:
                    print "Create rel. %s" % (unicode(tobj))
        return obj,flag

    def mk_morphologicalrule(self,v,vid):
        if v[0]!='AAA': return None,False
        dentry=v[1]
        reg=self.regexpreplacement[v[2]]
        name=v[3]
        dentry=(dentry=="1")
        try:
            qset=MorphologicalRule.objects.filter_classifications(self.objclass["morphologicalrule"][vid])
            obj=qset.get(regexp=reg)
            flag=False
        except MultipleObjectsReturned, e:
            try:
                obj=qset.filter(regexp=reg).get(name=name)
                flag=False
            except ObjectDoesNotExist, e:
                obj=MorphologicalRule.objects.create(regexp=reg,name=name,dict_entry=dentry)
                flag=True
        except ObjectDoesNotExist, e:
            obj=MorphologicalRule.objects.create(regexp=reg,name=name,dict_entry=dentry)
            flag=True
        if flag:
            for (cls,negate) in self.objclass["morphologicalrule"][vid]:
                tobj,created=MorhpologicalRuleClassification.objects.get_or_create(morphologicalrule=obj,classification=cls,negate=negate)
                if created:
                    print "Create rel. %s" % (unicode(tobj))
        return obj,flag
            
    def mk_paradigma(self,v,vid):
        if v[0]!='AAA': return None,False
        cat=self.category[v[1]]
        pos=self.partofspeech[v[2]]
        name=v[3]
        obj,created=Paradigma.objects.get_or_create(language=self.language,name=name,category=cat,part_of_speech=pos)
        obj.morphologicalrule_set.clear()
        if not self.parmr.has_key(vid):
            return obj,created
        for mr in self.parmr[vid]:
            obj.morphologicalrule_set.add(mr)
        return obj,created

    def mk_capitalizedword(self,v,vid):
        cl=self.classification[v[0]]
        pos=self.partofspeech[v[1]]
        return CapitalizedWord.objects.get_or_create(language=self.language,classification=cl,part_of_speech=pos)

    def mk_category(self,v,vid):
        return Category.objects.get_or_create(name=v[0])

    def mk_partofspeech(self,v,vid):
        return PartOfSpeech.objects.get_or_create(name=v[0])

    def mk_regexpreplacement(self,v,vid): 
        return RegexpReplacement.objects.get_or_create(pattern=v[0],replacement=v[1])

    def mk_classification(self,v,vid): 
        vcat=self.category[v[0]]
        return Classification.objects.get_or_create(category=vcat,exponent=v[1])

    def mk_objects(self,name):
        ret={}
        for v in self.comp[name]:
            t=v.split(':')
            vid=t[0]
            obj,created=self.mk_functions[name](t[1:],vid)
            if created:
                print "Create %s: %s" % (name,unicode(obj))
            if obj:
                ret[vid]=obj
        return(ret)

##### language

def get_or_create_language(comp):
    k='case_set'
    caseset_pairs_def=[]
    for v in comp[k]:
        t=v.split(":")
        if t[1]=="AAA":
            caseset_name=t[2]
            continue
        caseset_pairs_def.append( (t[2],t[3]) )

    k='tokenregexpset'
    tokenregexpset_regexps_def=[]
    for v in comp[k]:
        t=v.split(":")
        if t[1]=="AAA":
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
            cpair,created=CasePair.objects.get_or_create(lower=lower,upper=upper)
            if created: print "Create %s: %s,%s" % ("case pair",lower,upper)
            if not cset.pairs.filter(id=cpair.id).exists():
                cset.pairs.add(cpair)

    def tokenregexps_add(tset,regs_def,period_id=None):
        ret=None
        for (tid,tname,tdisabled,torder,tfg,tbg,tregexp) in regs_def:
            torder=int(torder)
            tdisabled=(tdisabled=='1')
            tr,created=TokenRegexp.objects.get_or_create(name=tname,regexp=tregexp)
            if created:    
                print "Create %s: %s,%s" % ("token regexp",tname,tregexp)

            trst,created=TokenRegexpSetThrough.objects.get_or_create(token_regexp=tr,token_regexp_set=tset,
                                                                     defaults={"bg_color":tbg,"fg_color":tfg,
                                                                               "order":torder,"disabled":tdisabled})
            if created:
                print "Create %s: %s/%d:%s" % ("token regexp set through",tset.name,torder,tname)
                                                          
            if period_id and tid==period_id: 
                ret=tr
        return(ret)
    
    try:
        language=Language.objects.get(name=langpar["name"])
        tokenregexpset=language.token_regexp_set
        caseset=language.case_set
        casepairs_add(caseset,caseset_pairs_def)
        tokenregexps_add(tokenregexpset,tokenregexpset_regexps_def)
    except ObjectDoesNotExist, e:
        caseset,created=CaseSet.objects.get_or_create(name=caseset_name)
        if created: print "Create %s: %s" % ("caseset",unicode(caseset))
        tokenregexpset,created=TokenRegexpSet.objects.get_or_create(name=tokenregexpset_name)
        if created: print "Create %s: %s" % ("tokenregexpset",unicode(tokenregexpset))
        casepairs_add(caseset,caseset_pairs_def)
        period_sep=tokenregexps_add(tokenregexpset,tokenregexpset_regexps_def,period_id=langpar["period_sep"])
        ao,created=AlphabeticOrder.objects.get_or_create(name=ao_name,order=ao_order)
        if created:
            print "Create %s: %s" % ("alphabetic order",ao_name)
        language=Language.objects.create(name=langpar["name"],token_regexp_set=tokenregexpset,case_set=caseset,
                                         period_sep=period_sep,alphabetic_order=ao)
    return(language)

class Command(BaseCommand):
    args = '<language>'
    help = 'Export <language>'

    def handle(self, *args, **options):
        fname=args[0]
        fd=open(fname,'r')
        text=fd.read()
        text=unicode(text,'utf-8')
        fd.close()
        
        lines=text.split('\n')

        comp={}

        for l in lines:
            if not l: continue
            if l[0]=='#': continue
            t=l.split(':')
            k=t[0]
            v=':'.join(t[1:])
            if not comp.has_key(k): comp[k]=[]
            comp[k].append(v)

        language=get_or_create_language(comp)

        impobjs=ImportObjects(language,comp)




