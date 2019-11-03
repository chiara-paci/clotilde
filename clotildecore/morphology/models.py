from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils.functional import cached_property
from django.utils.safestring import mark_safe
# Create your models here.

import re

from base import models as base_models
from languages import models as lang_models
from base import descriptions,functions

def combine(list_of_list):
    if len(list_of_list)==0: return []
    if len(list_of_list)==1: 
        return [ [x] for x in list_of_list[0] ]
    A=list_of_list[0]
    B=combine(list_of_list[1:])
    ret=[]
    for x in A:
        for y in B:
            ret.append( [x]+y )
    return ret

class RegexpReplacementManager(models.Manager):
    def update_reverse(self):
        for obj in self.all():
            #if hasattr(obj,"reverse"): continue
            RegexpReverse.objects.add_reverse(obj)
                
    def de_serialize(self,data):
        regsub,created=self.get_or_create(pattern=data["pattern"],
                                          replacement=data["replacement"])
        if "reverse" in data:
            rev,created=RegexpReverse.objects.update_or_create(target=regsub,defaults=data["reverse"])
        return regsub

class RegexpReplacement(models.Model):
    pattern=models.CharField(max_length=1024)
    replacement=models.CharField(max_length=1024)

    objects=RegexpReplacementManager()

    class Meta:
        ordering = ["pattern","replacement"]
        #unique_together = [ ["pattern","replacement"] ]

    def __str__(self):
        return "%s => %s" % (self.pattern,self.replacement)

    def apply(self,text):
        q=re.sub(self.pattern,self.replacement,text)
        return q

    def serialize(self):
        ret={
            "pattern": self.pattern,
            "replacement": self.replacement,
        }
        
        if hasattr(self,"reverse"):
            ret["reverse"]={
                "pattern": self.reverse.pattern,
                "replacement": self.reverse.replacement,
            }

        return ret

    class Meta:
        ordering = ["pattern","replacement"]

    @cached_property
    def num_inflections(self): return self.inflection_set.count()

    @cached_property
    def num_derivations(self): return self.derivation_set.count()

    @cached_property
    def num_fusion_rules(self): return self.fusionrule_set.count()


class RegexpReverseManager(models.Manager):

    def _add_N0(self,target):
        rev,created=self.update_or_create(target=target,
                                          defaults={
                                              "pattern":target.replacement,
                                              "replacement":target.replacement
                                          })
        return rev

    def _add_N1(self,target):
        N=target.replacement.count('\\1')
        if N==0:
            print("N==0",N,target)
            return None
        M=target.pattern.count(r'(')
        if M!=1:
            print("M!=1",M,target)
            return None
        base=""
        base_list=[ r'(.+)', r'(.+?)', r'(.)' ]
        for b in base_list:
            M=target.pattern.count(b)
            if M!=1: continue
            base=b
            break
        if not base:
            print("B   ",base_list,target)
            return
        rev_pattern=target.replacement.replace(r'\1',base)
        rev_replacement=target.pattern.replace(base,r'\1')
        rev,created=self.update_or_create(target=target,
                                          defaults={
                                              "pattern":rev_pattern,
                                              "replacement":rev_replacement
                                          })
        return rev
        
    def _add_N2(self,target):
        N1=target.replacement.count('\\1')
        N2=target.replacement.count('\\2')
        if N1!=1 or N2!=1:
            print("N!=1",N1,N2,target)
            return None

        if target.pattern not in [ '(.+)(.)', '(.)(.+)' ]:
            print("P2  ",target)

        if target.pattern=='(.+)(.)':
            rev_pattern=target.replacement.replace(r'\1',r'(.+)').replace(r'\2',r'(.)')
        else:
            rev_pattern=target.replacement.replace(r'\2',r'(.+)').replace(r'\1',r'(.)')

        rev_replacement=r'\1\2'
        rev,created=self.update_or_create(target=target,
                                          defaults={
                                              "pattern":rev_pattern,
                                              "replacement":rev_replacement
                                          })
        return rev
        
    def _add_N3(self,target):
        N1=target.replacement.count('\\1')
        N2=target.replacement.count('\\2')
        if N1>2 or N2>2:
            print("N!=2",N1,N2,target)
            return None
        if target.pattern not in [ '(.+)(.)', '(.)(.+)' ]:
            print("P3  ",target)
        
        if target.pattern=='(.+)(.)':
            p1=r'(.+)'
            p2=r'(.)'
        else:
            p1=r'(.)'
            p2=r'(.+)'

        if N1==2:
            rev_pattern=target.replacement.replace(r'\1\1',r'%s\1' % p1)
            rev_pattern=rev_pattern.replace(r'\2',p2)
        else:
            rev_pattern=target.replacement.replace(r'\2\2',r'%s\2' % p2)
            rev_pattern=rev_pattern.replace(r'\1',p1)


        rev_replacement=r'\1\2'
        rev,created=self.update_or_create(target=target,
                                          defaults={
                                              "pattern":rev_pattern,
                                              "replacement":rev_replacement
                                          })
        return rev
        

    def add_reverse(self,target):
        N=target.replacement.count('\\')
        if N==0:
            rev=self._add_N0(target)
            return
        if N==1:
            rev=self._add_N1(target)
            return
        if N==2:
            rev=self._add_N2(target)
            return
        if N==3:
            rev=self._add_N3(target)
            return
        print("N>3 ",N,target)
        return


class RegexpReverse(models.Model):
    target=models.OneToOneField(RegexpReplacement,on_delete=models.CASCADE,related_name="reverse")
    pattern=models.CharField(max_length=1024)
    replacement=models.CharField(max_length=1024)

    objects=RegexpReverseManager()

    def __str__(self):
        return "%s => %s" % (self.pattern,self.replacement)

class PartOfSpeech(base_models.AbstractName):
    bg_color = models.CharField(max_length=20,default="#ffff00")
    fg_color = models.CharField(max_length=20,default="#000000")

    def serialize(self):
        return (self.name, {
            "bg_color": self.bg_color,
            "fg_color": self.fg_color,
        })

##### Tema
    
class TemaArgument(base_models.AbstractName):
    @cached_property
    def num_entries(self):
        return self.temaentry_set.all().count()

    
class TemaValue(base_models.AbstractName): 
    @cached_property
    def num_entries(self):
        return self.temaentry_set.all().count()

    @cached_property
    def temas(self):
        T=" </li><li> ".join([ d.name for d in Tema.objects.filter(temaentryrelation__entry__value=self).distinct() ])
        return mark_safe("<ul><li>"+T+"</li></ul>")

class TemaManager(models.Manager):
    def by_language(self,lang_pk):
        q_or=models.Q(root__language__pk=lang_pk)
        q_or=q_or|models.Q(derivation__language__pk=lang_pk)
        q_or=q_or|models.Q(fusionrule__fusionrulerelation__fusion__language__pk=lang_pk)
        return self.filter(q_or).distinct()
    
    def by_part_of_speech(self,part_of_speech):
        if type(part_of_speech) is str:
            pos=PartOfSpeech.objects.filter(name=part_of_speech)[0]
        else:
            pos=part_of_speech
        der_qset=Root.objects.filter(part_of_speech=pos).values("tema_obj")
        return self.filter(pk__in=[ x["tema_obj"] for x in der_qset ])

    def de_serialize(self,ser):
        name,data=ser
        tema,created=Tema.objects.get_or_create(name=name)
        ok=[]
        for k,v in data[name]:
            attr,created=TemaArgument.objects.get_or_create(name=k)
            val,created=TemaValue.objects.get_or_create(name=v)
            entry,created=TemaEntry.objects.get_or_create(argument=attr,value=val) #,tema=tema)
            entryrel,created=TemaEntryRelation.objects.get_or_create(tema=tema,entry=entry)
            ok.append(entryrel.pk)
        TemaEntryRelation.objects.filter(tema=tema).exclude(pk__in=ok).delete()
        return tema

class Tema(base_models.AbstractName):
    objects = TemaManager()

    class Meta:
        ordering = [ "name" ]
    
    def _multidict(self,tlist):
        D={}
        for k,v in tlist:
            if k not in D: 
                D[k]=v
                continue
            if type(D[k]) is not set:
                D[k]=set( [D[k]] )
            D[k].add(v)
        return D

    def get_absolute_url(self):
        return "/morphology/tema/%d/" % self.pk
    
    def build(self):
        kwargs=self._multidict( [ (str(e.argument), str(e.value)) for e in self.temaentryrelation_set.all() ])
        return descriptions.Tema(**kwargs)

    def serialize(self):
        return (self.name, [ (str(e.argument), str(e.value)) for e in self.temaentryrelation_set.all() ] ) 

    @cached_property
    def num_entries(self):
        return self.temaentryrelation_set.all().count()
    
    @cached_property
    def num_roots(self):
        return self.root_set.all().count()

    @cached_property
    def num_derivations(self):
        qs_der=Derivation.objects.filter(tema_entry__in=self.temaentryrelation_set.all().values("entry"))
        return qs_der.count()

    @cached_property
    def num_fusion_rules(self):
        return self.fusionrule_set.all().count()

    @cached_property
    def num_references(self):
        return self.num_roots+self.num_fusion_rules #+self.num_derivations

    @cached_property
    def derivations(self):
        qs_der=Derivation.objects.filter(tema_entry__in=self.temaentryrelation_set.all().values("entry"))
        return "; ".join([ d.name for d in qs_der ])

    @cached_property
    def roots(self):
        return "; ".join([ r.root for r in self.root_set.all() ])

class TemaEntry(models.Model):
    #tema = models.ForeignKey(Tema,on_delete=models.CASCADE)    
    argument = models.ForeignKey(TemaArgument,on_delete=models.CASCADE)    
    value = models.ForeignKey(TemaValue,on_delete=models.CASCADE)    

    def __str__(self):
        return "%s=%s" % (str(self.argument),str(self.value))

    class Meta:
        ordering=["argument","value"]
        unique_together=[ ["argument","value"] ]

    @cached_property
    def num_temas(self): return self.temaentryrelation_set.count()

    @cached_property
    def num_derivations(self): return self.derivation_set.count()

class TemaEntryRelation(models.Model):
    tema = models.ForeignKey(Tema,on_delete=models.CASCADE)    
    entry = models.ForeignKey(TemaEntry,on_delete=models.CASCADE)    

    def __str__(self):
        return str(self.entry)

    class Meta:
        ordering=["entry"]

    @cached_property
    def argument(self): return self.entry.argument

    @cached_property
    def value(self): return self.entry.value


#####
    
class ParadigmaManager(models.Manager):
    def by_language(self,lang_pk):
        return self.filter(language__pk=lang_pk)

class Paradigma(base_models.AbstractName):
    part_of_speech = models.ForeignKey(PartOfSpeech,on_delete=models.PROTECT)    
    language = models.ForeignKey('languages.Language',on_delete=models.PROTECT)    
    inflections = models.ManyToManyField("Inflection",blank=True)

    objects=ParadigmaManager()

    class Meta:
        ordering = ["name"]

    def get_absolute_url(self):
        return "/morphology/paradigma/%d/" % self.pk

    @cached_property
    def count_roots(self):
        return Root.objects.filter(stem__derivation__paradigma=self).distinct().count()

    @cached_property
    def count_words(self):
        return Word.objects.filter(stem__derivation__paradigma=self).distinct().count()

    @cached_property
    def count_stems(self):
        return Stem.objects.filter(derivation__paradigma=self).distinct().count()

    @cached_property
    def count_derivations(self):
        return self.derivation_set.count()

    @cached_property
    def count_inflections(self):
        return self.inflections.count()

    def split_inflections(self,arg_list):

        qset=Inflection.objects.filter(paradigma=self)
        kwargs={}
        for k in arg_list:
            kwargs[k]= models.Max("description_obj__entries__value__string",filter=models.Q(description_obj__entries__attribute__name=k))
        qset=qset.annotate(**kwargs)

        ret={}
        for infl in qset:
            key=tuple( [ x if x is not None else "-" for x in [ getattr(infl,k) for k in arg_list ] ])
            print(key)
            if key not in ret: ret[key]=[]
            ret[key].append(infl)
        return ret

class Inflection(models.Model):
    dict_entry = models.BooleanField(default=False)
    regsub = models.ForeignKey(RegexpReplacement,on_delete=models.PROTECT)    
    description_obj = models.ForeignKey(base_models.Description,on_delete=models.PROTECT)

    class Meta:
        ordering = ["regsub"]

    @cached_property
    def description(self):
        return self.description_obj.build()

    def __str__(self):
        if not self.dict_entry:
            return "%s [%s]" % (self.regsub,self.description)
        return "%s [%s] [DICT]" % (self.regsub,self.description)

    @cached_property
    def num_paradigmas(self):
        return self.paradigma_set.count()

    def serialize(self):
        return {
            "dict_entry": self.dict_entry,
            "regsub": self.regsub.serialize(),
            "description": self.description_obj.name
        }

class RootManager(models.Manager):

    def de_serialize(self,ser):
        try:
            obj,created=Root.objects.get_or_create(root=ser["root"],
                                                   part_of_speech=ser["part_of_speech"],
                                                   tema_obj=ser["tema"],
                                                   language=ser["language"])
        except Exception as e:
            print(ser)
            raise e
        return obj

    def by_language(self,lang_pk):
        return self.filter(language__pk=lang_pk)

    def _clean_fused(self,language,root_list=None):
        if root_list is None:
            FusedWordRelation.objects.filter(fused_word__fusion__language=language).delete()
            FusedWord.objects.filter(fusion__language=language).delete()
            return
        fword_list=list(FusedWord.objects.filter(fusedwordrelation__word__stem__root__in=root_list))
        FusedWordRelation.objects.filter(fused_word__in=fword_list).delete()
        for fword in fword_list:
            fword.delete()

    def _rebuild_fused(self,language,root_list=None):
        if root_list is None:
            FusedWord.objects.rebuild(language)
            return
        qset=Word.objects.filter(stem__root__in=root_list)
        qset=qset.values("inflection__paradigma__part_of_speech")
        qset=qset.order_by("inflection__paradigma__part_of_speech").distinct()
        fpk_qset=FusionRuleRelation.objects.filter(fusion_rule__part_of_speech__in=qset)
        fpk_qset=fpk_qset.values("fusion__pk")
        fusion_list=Fusion.objects.filter(pk__in=fpk_qset)
        FusedWord.objects.rebuild(language,fusion_list=fusion_list)
        
    def clean_derived_tables(self,language,root_names):
        if root_names:
            root_list=self.filter(language=language,root__in=root_names)
            self._clean_fused(language,root_list)
        else:
            root_list=self.filter(language=language)
            self._clean_fused(language)
        Word.objects.filter(stem__root__in=root_list).delete()
        Stem.objects.filter(root__in=root_list).delete()

    def update_derived_tables(self,language,root_names=[],fused=True):
        if not root_names:
            root_list=self.filter(language=language)
            queryset_word=Word.objects.filter(stem__root__language=language)
            queryset_stem=Stem.objects.filter(root__language=language)
            if fused: self._clean_fused(language)
        else:
            root_list=self.filter(language=language,root__in=root_names)
            queryset_word=Word.objects.filter(stem__root__language=language,
                                              stem__root__in=root_list)
            queryset_stem=Stem.objects.filter(root__language=language,
                                              root__in=root_list)
            if fused: self._clean_fused(language,root_list)

        # phase 1. stems
        der_list=Derivation.objects.filter(language=language)
        ok=[]
        for root in root_list:
            print("R",root,"(%s)" % root.part_of_speech)
            for der in der_list:
                if root.part_of_speech != der.root_part_of_speech: continue
                if not (der.tema <= root.tema): continue
                #if not (der.root_description <= root.description): continue
                stem,created=Stem.objects.get_or_create(root=root,derivation=der)
                stem.clean()
                stem.save()
                ok.append(stem.pk)
        queryset_word.exclude(stem__pk__in=ok).delete()
        queryset_stem.exclude(pk__in=ok).delete()
 
        # phase 2. words
        stem_list=queryset_stem.all()
        #par_list=Paradigma.objects.filter(language=language)
 
        ok=[]
        for stem in stem_list:
            print("    S",stem,"(%s)" % stem.part_of_speech)
            for infl in stem.paradigma.inflections.all():
                word,created=Word.objects.get_or_create(stem=stem,inflection=infl)
                word.clean()
                word.save()
                print("        W %-20.20s %s" % (str(word),str(word.description)))
                ok.append(word.pk)
        queryset_word.exclude(pk__in=ok).delete()

        # phase 3. fused words

        if not fused: return

        if not root_names:
            self._rebuild_fused(language)
            return
        self._rebuild_fused(language,root_list)


class Root(models.Model):
    root=models.CharField(max_length=1024)
    language = models.ForeignKey('languages.Language',on_delete=models.PROTECT)    
    tema_obj = models.ForeignKey(Tema,on_delete=models.PROTECT)    
    part_of_speech = models.ForeignKey(PartOfSpeech,on_delete=models.PROTECT)    
    # description_obj = models.ForeignKey(base_models.Description,on_delete=models.PROTECT)    

    objects=RootManager()

    class Meta:
        ordering = ["root"]
        unique_together = [ ["language","root","tema_obj","part_of_speech"] ] #,"description_obj"] ]

    def __str__(self):
        return "%s (%s)" % (self.root,self.part_of_speech)

    # @cached_property
    # def description(self):
    #     return self.description_obj.build()

    @cached_property
    def tema(self):
        return self.tema_obj.build()

    def serialize(self):
        return {
            "root": self.root,
            "tema": self.tema_obj.name,
            # "description": self.description_obj.name,
            "part_of_speech": self.part_of_speech.name,
        }

    def get_absolute_url(self):
        return "/morphology/root/%d/" % self.pk

    def update_derived(self):
        queryset_word=Word.objects.filter(stem__root=self)
        queryset_stem=Stem.objects.filter(root=self)

        # phase 1. stems
        der_list=Derivation.objects.filter(language=self.language,
                                           root_part_of_speech=self.part_of_speech)
        ok=[]
        for der in der_list:
            if not (der.tema <= self.tema): continue
            #if not (der.root_description <= self.description): continue
            stem,created=Stem.objects.get_or_create(root=self,derivation=der)
            stem.clean()
            stem.save()
            print("S",stem)
            ok.append(stem.pk)
        queryset_word.exclude(stem__pk__in=ok).delete()
        queryset_stem.exclude(pk__in=ok).delete()
 
        # phase 2. words
        stem_list=queryset_stem.all()
        ok=[]
        for stem in stem_list:
            for infl in stem.paradigma.inflections.all():
                word,created=Word.objects.get_or_create(stem=stem,inflection=infl)
                word.clean()
                word.save()
                print("W",word)
                ok.append(word.pk)
        queryset_word.exclude(pk__in=ok).delete()

        # phase 3. fused words

        #FusedWord.objects.rebuild(language)
    
class DerivationManager(models.Manager):
    def by_language(self,lang_pk):
        return self.filter(language__pk=lang_pk)

    def de_serialize(self,ser):
        language,name,data=ser
        defaults={}
        for k in [ "regsub","root_part_of_speech","paradigma" ]:
            defaults[k]=data[k]
        # for k in [ "tema","description" ]:
        for k in [ "description" ]:
            defaults[k+"_obj"]=data[k]

        a,v=data["tema_entry"]
        attr,created=TemaArgument.objects.get_or_create(name=a)
        val,created=TemaValue.objects.get_or_create(name=v)
        entry,created=TemaEntry.objects.get_or_create(argument=attr,value=val) #,tema=tema)
        defaults["tema_entry"]=entry
        der,created=Derivation.objects.update_or_create(name=name,language=language,
                                                        defaults=defaults)
        return der


class Derivation(base_models.AbstractName):
    language = models.ForeignKey('languages.Language',on_delete=models.PROTECT)    
    regsub = models.ForeignKey(RegexpReplacement,on_delete=models.PROTECT)    
    # tema_obj = models.ForeignKey(Tema,on_delete=models.PROTECT)    
    tema_entry = models.ForeignKey(TemaEntry,on_delete=models.PROTECT)    
    description_obj = models.ForeignKey(base_models.Description,on_delete=models.PROTECT)    
    # root_description_obj = models.ForeignKey(base_models.Description,
    #                                          on_delete=models.PROTECT,
    #                                          related_name="root_derivation_set")    
    root_part_of_speech = models.ForeignKey(PartOfSpeech,on_delete=models.PROTECT)    
    paradigma = models.ForeignKey(Paradigma,on_delete=models.PROTECT)

    objects=DerivationManager()

    class Meta:
        ordering = ['name']

    def serialize(self):
        return (self.name,{
            "regsub": self.regsub.serialize(),
            # "tema": self.tema_obj.name,
            "description": self.description_obj.name,
            # "root_description": self.root_description_obj.name,
            "root_part_of_speech": self.root_part_of_speech.name,
            "paradigma": self.paradigma.name,
            "tema_entry": ( str(self.tema_entry.argument), str(self.tema_entry.value) )
        })

    @cached_property
    def num_stem(self):
        return self.stem_set.count()

    @cached_property
    def description(self):
        return self.description_obj.build()

    @cached_property
    def part_of_speech(self):
        return self.paradigma.part_of_speech

    # @cached_property
    # def root_description(self):
    #     return self.root_description_obj.build()

    @cached_property
    def tema(self):
        kwargs=dict( [ (str(self.tema_entry.argument), str(self.tema_entry.value)) ])
        return descriptions.Tema(**kwargs)

    # @cached_property
    # def num_tema_entries(self):
    #     return self.tema_obj.num_entries

    def clean(self):
        if self.language != self.paradigma.language:
            raise ValidationError(_('Paradigma and language are not compatible.'))

    def get_absolute_url(self):
        return "/morphology/derivation/%d/" % self.pk

class FusionManager(models.Manager):
    def by_language(self,lang_pk):
        return self.filter(language__pk=lang_pk)
    
class Fusion(base_models.AbstractName):
    language = models.ForeignKey('languages.Language',on_delete=models.PROTECT)    
    objects=FusionManager()

class FusionRule(base_models.AbstractName):
    regsub = models.ForeignKey(RegexpReplacement,on_delete=models.PROTECT)    
    tema_obj = models.ForeignKey(Tema,on_delete=models.PROTECT)    
    part_of_speech = models.ForeignKey(PartOfSpeech,on_delete=models.PROTECT)    
    description_obj = models.ForeignKey(base_models.Description,on_delete=models.PROTECT)    

    @cached_property
    def description(self):
        return self.description_obj.build()

    @cached_property
    def tema(self):
        return self.tema_obj.build()

    @cached_property
    def num_fusions(self):
        return self.fusionrulerelation_set.all().count()
    
    def serialize(self):
        return {
            "name": self.name,
            "regsub": self.regsub.serialize(),
            "tema": self.tema_obj.name,
            "description": self.description_obj.name,
            "part_of_speech": self.part_of_speech.name,
        }


class FusionRuleRelation(models.Model):
    fusion = models.ForeignKey(Fusion,on_delete=models.CASCADE)    
    fusion_rule = models.ForeignKey(FusionRule,on_delete=models.CASCADE)    
    order = models.IntegerField()

    def __str__(self):
        return "%s/%s(%d)" % (self.fusion,self.fusion_rule,self.order) 

    class Meta:
        ordering = [ "order" ]

class StemManager(models.Manager):
    def by_language(self,lang_pk):
        return self.filter(root__language__pk=lang_pk)

class Stem(models.Model):
    root = models.ForeignKey(Root,on_delete=models.CASCADE)    
    derivation = models.ForeignKey(Derivation,on_delete=models.CASCADE)    
    cache=models.CharField(max_length=1024,db_index=True,editable=False)

    objects=StemManager()
    
    class Meta:
        ordering = ["cache"]

    def __str__(self): return self.cache

    def clean(self):
        if self.root.language != self.derivation.language:
            raise ValidationError(_('Root and derivation are not compatible (language).'))
        if self.root.part_of_speech != self.derivation.root_part_of_speech:
            raise ValidationError(_('Root and derivation are not compatible (part of speech).'))
        dtema=self.derivation.tema
        rtema=self.root.tema
        if not dtema<=rtema: 
            raise ValidationError(_('Root and derivation are not compatible (tema).'))
        # ddesc=self.derivation.root_description
        # rdesc=self.root.description
        # if not ddesc<=rdesc: 
        #     raise ValidationError(_('Root and derivation are not compatible (description).'))
        # if self.status == 'published' and self.pub_date is None:
        #     self.pub_date = datetime.date.today()
        self.cache=self.derivation.regsub.apply(self.root.root)

        
    @cached_property
    def description(self): return self.derivation.description
        # ddesc=self.derivation.description
        # #rdesc=self.root.description
        # return ddesc+rdesc

    @cached_property
    def stem(self): return self.cache

    @cached_property
    def tema(self): return self.root.tema

    @cached_property
    def paradigma(self): return self.derivation.paradigma

    @cached_property
    def language(self): return self.derivation.language

    @cached_property
    def part_of_speech(self): return self.derivation.paradigma.part_of_speech

    @cached_property
    def dictionary_voice(self):
        return ", ".join([str(w) for w in self.word_set.filter(inflection__dict_entry=True)])
    
class WordManager(models.Manager): pass

class Word(models.Model):
    stem = models.ForeignKey(Stem,on_delete=models.CASCADE)    
    inflection = models.ForeignKey(Inflection,on_delete=models.CASCADE)    
    cache=models.CharField(max_length=1024,db_index=True,editable=False)

    objects=WordManager()

    class Meta:
        ordering = [ "cache" ]

    def __str__(self): return self.cache

    def clean(self):
        if not self.inflection in self.stem.paradigma.inflections.all():
            raise ValidationError(_('Stem and inflection are not compatible (inflection not in paradigma).'))
        self.cache=self.inflection.regsub.apply(self.stem.stem)

    @cached_property
    def description(self):
        try:
            idesc=self.inflection.description
            sdesc=self.stem.description
            return idesc+sdesc
        except descriptions.FailedUnification as e:
            return descriptions.Description(failed=str(e))

    @cached_property
    def tema(self): return self.stem.tema

    @cached_property
    def part_of_speech(self): return self.stem.part_of_speech
    
    @cached_property
    def dict_entry(self): return self.inflection.dict_entry

    @cached_property
    def paradigma(self): return self.stem.paradigma

    @cached_property
    def language(self): return self.stem.language


class FusedWordManager(models.Manager):


    ### QUI
    def _reduce_word_list(self,part_of_speech,tema,description):
        """ This function is just a performance booster, not a perfect filter,
            and retrieves more words than  necessary (but still not all
            words).
        """

        qset=Word.objects.filter(stem__derivation__paradigma__part_of_speech=part_of_speech)        
        for arg in tema:
            if tema[arg] not in [list,set]:
                qtentry=TemaEntryRelation.objects.filter(entry__argument__name=arg,entry__value__name=tema[arg])
                qset=qset.filter(stem__root__tema_obj__in=[x["tema"] for x in qtentry.values("tema")])
                continue
            for val in tema[arg]:
                qtentry=TemaEntryRelation.objects.filter(entry__argument__name=arg,entry__value__name=val)
                qset=qset.filter(stem__root__tema_obj__in=[x["tema"] for x in qtentry.values("tema")])

        for arg in description:
            if isinstance(description[arg],descriptions.Description): continue
            if type(description[arg]) is tuple:
                if description[arg][1]: continue
                val=description[arg][0]
            else:
                val=description[arg]
            qentry=base_models.Entry.objects.filter( models.Q(attribute__name=arg,
                                                              value__string=val,invert=False) )
            desc_list=[x["description"] for x in  qentry.values("description")] 
            # query= models.Q(stem__derivation__description_obj__in=desc_list) | \
            #     models.Q(stem__root__description_obj__in=desc_list) | \
            #     models.Q(inflection__description_obj__in=desc_list) 
            query= models.Q(stem__derivation__description_obj__in=desc_list) | \
                models.Q(inflection__description_obj__in=desc_list) 
            qset=qset.filter(query)
        return qset


    def rebuild(self,language,fusion_list=[]):
        # FusedWordRelation.objects.filter(fused_word__fusion__language=language).delete()
        # self.filter(fusion__language=language).delete()
        # fusion_list=Fusion.objects.filter(language=language)
        if not fusion_list:
            fusion_list=Fusion.objects.filter(language=language)

        FusedWordRelation.objects.filter(fused_word__fusion__in=fusion_list).delete()
        self.filter(fusion__in=fusion_list).delete()

        ok=[]
        for fusion in fusion_list:
            print(fusion)
            comp=[]
            abort=False
            for rel in fusion.fusionrulerelation_set.all().order_by("order"):
                rule=rel.fusion_rule
                word_list=self._reduce_word_list(rule.part_of_speech,rule.tema,rule.description)
                w_comp=[]
                print("    rule %s: tema=%s, description=%s" % (rule,str(rule.tema),str(rule.description) ) )
                print("        ",word_list)
                for w in word_list:
                    if not (rule.tema <= w.tema): continue
                    if not (rule.description <= w.description): continue
                    w_comp.append(w)
                if not w_comp:
                    abort=True
                    break
                comp.append( w_comp )
            if abort: continue

            comp=combine(comp)
            for w_list in comp:
                print("    F:",w_list)
                fword=FusedWord(fusion=fusion)
                fword.save()
                n=0
                for w in w_list:
                    fwrel=FusedWordRelation(fused_word=fword,word=w,order=n)
                    fwrel.full_clean()
                    fwrel.save()
                    n+=1
                fword.full_clean()
                fword.save()
                print("        = %20s" % fword)

class FusedWord(models.Model):
    fusion = models.ForeignKey(Fusion,on_delete=models.CASCADE)    
    cache = models.CharField(max_length=1024,db_index=True,editable=False)
    objects=FusedWordManager()

    def clean(self):
        S=""
        n=0
        for word in [ rel.word for rel in self.fusedwordrelation_set.all().order_by("order") ]:
            rule=self.rules[n]
            #print("   ",word,rule)
            res=rule.regsub.apply(word.cache)
            print("        W %20s %20s %20s" % (word.cache,rule.regsub,res) )
            S+=res
            n+=1
        self.cache=S

    def __str__(self): return self.cache

    @cached_property
    def rules(self):
        return [ rel.fusion_rule for rel in self.fusion.fusionrulerelation_set.all().order_by("order") ]

    @cached_property
    def words(self):
        return [ rel.word for rel in self.fusedwordrelation_set.all().order_by("order") ]
        
    @cached_property
    def description(self): return [ w.description for w in self.words ]

    @cached_property
    def tema(self):  return [ w.tema for w in self.words ]

    @cached_property
    def part_of_speech(self): return [ w.part_of_speech for w in self.words ]
    
    @cached_property
    def language(self): return self.fusion.language


class FusedWordRelation(models.Model):
    fused_word = models.ForeignKey(FusedWord,on_delete=models.CASCADE)    
    word = models.ForeignKey(Word,on_delete=models.CASCADE)    
    order = models.IntegerField()

    def __str__(self):
        return "%s/%s" % (self.fused_word.cache,self.word.cache)

    def clean(self):
        if self.word.language != self.fused_word.language:
            raise ValidationError(_('Fused word and word are not compatible (language).'))
        rule=self.fused_word.rules[self.order]
        if self.word.part_of_speech != rule.part_of_speech:
            raise ValidationError(_('Rule %d and word are not compatible (part of speech).' % self.order))
        dtema=rule.tema
        rtema=self.word.tema
        if not dtema<=rtema: 
            raise ValidationError(_('Rule %d and word are not compatible (tema).' % self.order ))
        ddesc=rule.description
        rdesc=self.word.description
        if not ddesc<=rdesc: 
            raise ValidationError(_('Rule %d and word are not compatible (description).' % self.order ))

    @cached_property
    def description(self): self.word.description

    @cached_property
    def tema(self): return self.word.tema

    @cached_property
    def part_of_speech(self): return self.word.part_of_speech
    
    @cached_property
    def language(self): return self.word.language
