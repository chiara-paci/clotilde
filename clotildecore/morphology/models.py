from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils.functional import cached_property

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

class RegexpReplacement(models.Model):
    pattern=models.CharField(max_length=1024)
    replacement=models.CharField(max_length=1024)

    class Meta:
        ordering = ["pattern","replacement"]
        #unique_together = [ ["pattern","replacement"] ]

    def __str__(self):
        return "%s => %s" % (self.pattern,self.replacement)

    def apply(self,text):
        q=re.sub(self.pattern,self.replacement,text)
        return q

    def serialize(self):
        return [ str(self.pattern),str(self.replacement) ]

    class Meta:
        ordering = ["pattern","replacement"]

    @cached_property
    def num_inflections(self): return self.inflection_set.count()

    @cached_property
    def num_derivations(self): return self.derivation_set.count()

    @cached_property
    def num_fusion_rules(self): return self.fusionrule_set.count()

class PartOfSpeech(base_models.AbstractName):
    bg_color = models.CharField(max_length=20,default="#ffff00")
    fg_color = models.CharField(max_length=20,default="#000000")

    def serialize(self):
        return (self.name, {
            "bg_color": self.bg_color,
            "fg_color": self.fg_color,
        })

class TemaArgument(base_models.AbstractName): pass
class TemaValue(base_models.AbstractName): pass

class TemaManager(models.Manager):
    def by_part_of_speech(self,part_of_speech):
        if type(part_of_speech) is str:
            pos=PartOfSpeech.objects.filter(name=part_of_speech)[0]
        else:
            pos=part_of_speech
        der_qset=Root.objects.filter(part_of_speech=pos).values("tema_obj")
        return self.filter(pk__in=[ x["tema_obj"] for x in der_qset ])

class Tema(base_models.AbstractName):
    objects = TemaManager()

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
    
    def build(self):
        kwargs=self._multidict( [ (str(e.argument), str(e.value)) for e in self.temaentry_set.all() ])
        return descriptions.Tema(**kwargs)

    def serialize(self):
        return (self.name, [ (str(e.argument), str(e.value)) for e in self.temaentry_set.all() ] ) 

    def num_roots(self):
        return self.root_set.all().count()

    def num_derivations(self):
        return self.derivation_set.all().count()

    def num_fusion_rules(self):
        return self.fusionrule_set.all().count()

    class Meta:
        ordering = [ "name" ]

class TemaEntry(models.Model):
    tema = models.ForeignKey(Tema,on_delete="cascade")    
    argument = models.ForeignKey(TemaArgument,on_delete="cascade")    
    value = models.ForeignKey(TemaValue,on_delete="cascade")    

    def __str__(self):
        return "%s=%s" % (str(self.argument),str(self.value))

    class Meta:
        ordering=["argument","value"]

class Paradigma(base_models.AbstractName):
    part_of_speech = models.ForeignKey(PartOfSpeech,on_delete="cascade")    
    language = models.ForeignKey('languages.Language',on_delete="cascade")    
    inflections = models.ManyToManyField("Inflection",blank=True)

    class Meta:
        ordering = ["name"]

    def get_absolute_url(self):
        return "/morphology/paradigma/%d/" % self.pk

    @cached_property
    def count_roots(self):
        return self.root_set.count()

    @cached_property
    def count_derivations(self):
        return self.derivation_set.count()

class Inflection(models.Model):
    dict_entry = models.BooleanField(default=False)
    regsub = models.ForeignKey(RegexpReplacement,on_delete="cascade")    
    description_obj = models.ForeignKey(base_models.Description,on_delete="cascade")

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
    def clean_derived_tables(self,language,root_names): 
        root_list=self.filter(language=language,root__in=root_names)
        Word.objects.filter(stem__root__in=root_list).delete()
        Stem.objects.filter(root__in=root_list).delete()

    def update_derived_tables(self,language,root_names=[],fused=True):
        if not root_names:
            root_list=self.filter(language=language)
            queryset_word=Word.objects.filter(stem__root__language=language)
            queryset_stem=Stem.objects.filter(root__language=language)
        else:
            root_list=self.filter(language=language,root__in=root_names)
            queryset_word=Word.objects.filter(stem__root__language=language,
                                              stem__root__in=root_list)
            queryset_stem=Stem.objects.filter(root__language=language,
                                              root__in=root_list)

        if fused:
            FusedWordRelation.objects.filter(fused_word__fusion__language=language).delete()
            FusedWord.objects.filter(fusion__language=language).delete()

        # phase 1. stems
        der_list=Derivation.objects.filter(language=language)
        ok=[]
        for root in root_list:
            print("R",root,"(%s)" % root.part_of_speech)
            for der in der_list:
                if root.part_of_speech != der.root_part_of_speech: continue
                if not (der.tema <= root.tema): continue
                if not (der.root_description <= root.description): continue
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
                print("        W",word)
                ok.append(word.pk)
        queryset_word.exclude(pk__in=ok).delete()

        # phase 3. fused words

        if fused:
            FusedWord.objects.rebuild(language)

class Root(models.Model):
    root=models.CharField(max_length=1024)
    language = models.ForeignKey('languages.Language',on_delete="cascade")    
    tema_obj = models.ForeignKey(Tema,on_delete="cascade")    
    part_of_speech = models.ForeignKey(PartOfSpeech,on_delete="cascade")    
    description_obj = models.ForeignKey(base_models.Description,on_delete="cascade")    

    objects=RootManager()

    class Meta:
        ordering = ["root"]
        unique_together = [ ["language","root","tema_obj","part_of_speech","description_obj"] ]

    def __str__(self):
        return "%s (%s)" % (self.root,self.part_of_speech)

    @cached_property
    def description(self):
        return self.description_obj.build()

    @cached_property
    def tema(self):
        return self.tema_obj.build()

    def serialize(self):
        return {
            "root": self.root,
            "tema": self.tema_obj.name,
            "description": self.description_obj.name,
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
            if not (der.root_description <= self.description): continue
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
    
    
class Derivation(base_models.AbstractName):
    language = models.ForeignKey('languages.Language',on_delete="cascade")    
    regsub = models.ForeignKey(RegexpReplacement,on_delete="cascade")    
    tema_obj = models.ForeignKey(Tema,on_delete="cascade")    
    description_obj = models.ForeignKey(base_models.Description,on_delete="cascade")    
    root_description_obj = models.ForeignKey(base_models.Description,
                                             on_delete="cascade",
                                             related_name="root_derivation_set")    
    root_part_of_speech = models.ForeignKey(PartOfSpeech,on_delete="cascade")    
    paradigma = models.ForeignKey(Paradigma,on_delete="cascade")    

    class Meta:
        ordering = ['name']

    def serialize(self):
        return (self.name,{
            "regsub": self.regsub.serialize(),
            "tema": self.tema_obj.name,
            "description": self.description_obj.name,
            "root_description": self.root_description_obj.name,
            "root_part_of_speech": self.root_part_of_speech.name,
            "paradigma": self.paradigma.name,
        })


    @cached_property
    def description(self):
        return self.description_obj.build()

    @cached_property
    def part_of_speech(self):
        return self.paradigma.part_of_speech

    @cached_property
    def root_description(self):
        return self.root_description_obj.build()

    @cached_property
    def tema(self):
        return self.tema_obj.build()

    def clean(self):
        if self.language != self.paradigma.language:
            raise ValidationError(_('Paradigma and language are not compatible.'))

    def get_absolute_url(self):
        return "/morphology/derivation/%d/" % self.pk


#class ParadigmaInflection(models.Model):
#    paradigma = models.ForeignKey(Paradigma,on_delete="cascade")    
#    inflection = models.ForeignKey(Inflection,on_delete="cascade")    

    
class Fusion(base_models.AbstractName):
    language = models.ForeignKey('languages.Language',on_delete="cascade")    
    #objects=FusionManager()

class FusionRule(base_models.AbstractName):
    regsub = models.ForeignKey(RegexpReplacement,on_delete="cascade")    
    tema_obj = models.ForeignKey(Tema,on_delete="cascade")    
    part_of_speech = models.ForeignKey(PartOfSpeech,on_delete="cascade")    
    description_obj = models.ForeignKey(base_models.Description,on_delete="cascade")    

    @cached_property
    def description(self):
        return self.description_obj.build()

    @cached_property
    def tema(self):
        return self.tema_obj.build()

    def serialize(self):
        return {
            "name": self.name,
            "regsub": self.regsub.serialize(),
            "tema": self.tema_obj.name,
            "description": self.description_obj.name,
            "part_of_speech": self.part_of_speech.name,
        }


class FusionRuleRelation(models.Model):
    fusion = models.ForeignKey(Fusion,on_delete="cascade")    
    fusion_rule = models.ForeignKey(FusionRule,on_delete="cascade")    
    order = models.IntegerField()

    def __str__(self):
        return "%s/%s(%d)" % (self.fusion,self.fusion_rule,self.order) 

    class Meta:
        ordering = [ "order" ]

class Stem(models.Model):
    root = models.ForeignKey(Root,on_delete="cascade")    
    derivation = models.ForeignKey(Derivation,on_delete="cascade")    
    cache=models.CharField(max_length=1024,db_index=True,editable=False)

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
        ddesc=self.derivation.root_description
        rdesc=self.root.description
        if not ddesc<=rdesc: 
            raise ValidationError(_('Root and derivation are not compatible (description).'))
        # if self.status == 'published' and self.pub_date is None:
        #     self.pub_date = datetime.date.today()
        self.cache=self.derivation.regsub.apply(self.root.root)

        
    @cached_property
    def description(self):
        ddesc=self.derivation.description
        rdesc=self.root.description
        return ddesc+rdesc

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
    
class WordManager(models.Manager): pass

class Word(models.Model):
    stem = models.ForeignKey(Stem,on_delete="cascade")    
    inflection = models.ForeignKey(Inflection,on_delete="cascade")    
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


    def _reduce_word_list(self,part_of_speech,tema,description):
        """ This function is just a performance booster, not a perfect filter,
            and retrieves more words than  necessary (but still not all
            words).
        """

        qset=Word.objects.filter(stem__derivation__paradigma__part_of_speech=part_of_speech)        
        for arg in tema:
            if tema[arg] not in [list,set]:
                qtentry=TemaEntry.objects.filter(argument__name=arg,value__name=tema[arg])
                qset=qset.filter(stem__root__tema_obj__in=[x["tema"] for x in qtentry.values("tema")])
                continue
            for val in tema[arg]:
                qtentry=TemaEntry.objects.filter(argument__name=arg,value__name=val)
                qset=qset.filter(stem__root__tema_obj__in=[x["tema"] for x in qtentry.values("tema")])

        for arg in description:
            if isinstance(description[arg],descriptions.Description): continue
            if type(description[arg]) is tuple:
                if description[arg][1]: continue
                val=description[arg][0]
            else:
                val=description[arg]
            qentry=base_models.Entry.objects.filter( models.Q(attribute__name=arg,value__string=val,invert=False) )
            desc_list=[x["description"] for x in  qentry.values("description")] 
            query= models.Q(stem__derivation__description_obj__in=desc_list) | \
                models.Q(stem__root__description_obj__in=desc_list) | \
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
                word_list=self._reduce_word_list(rule.part_of_speech,rule.tema,rule.description) #   Word.objects.filter(stem__derivation__paradigma__part_of_speech=rule.part_of_speech)
                w_comp=[]
                print("    rule %s: tema=%s, description=%s" % (rule,str(rule.tema),str(rule.description) ) )
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
    fusion = models.ForeignKey(Fusion,on_delete="cascade")    
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
    fused_word = models.ForeignKey(FusedWord,on_delete="cascade")    
    word = models.ForeignKey(Word,on_delete="cascade")    
    order = models.IntegerField()

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
