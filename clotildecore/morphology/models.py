from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils.functional import cached_property

# Create your models here.

import re

from base import models as base_models
from languages import models as lang_models
from base import descriptions

class RegexpReplacement(models.Model):
    pattern=models.CharField(max_length=1024)
    replacement=models.CharField(max_length=1024)

    def __str__(self):
        return "%s => %s" % (self.pattern,self.replacement)

    def apply(self,text):
        q=re.sub(self.pattern,self.replacement,text)
        return q

    def serialize(self):
        return [ str(self.pattern),str(self.replacement) ]

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

class Tema(base_models.AbstractName):
    def build(self):
        kwargs={ str(e.argument): str(e.value) for e in self.temaentry_set.all() }
        return descriptions.Description(**kwargs)

    def serialize(self):
        return (self.name,{ str(e.argument): str(e.value) for e in self.temaentry_set.all() })

class TemaEntry(models.Model):
    tema = models.ForeignKey(Tema,on_delete="cascade")    
    argument = models.ForeignKey(TemaArgument,on_delete="cascade")    
    value = models.ForeignKey(TemaValue,on_delete="cascade")    

class Paradigma(base_models.AbstractName):
    part_of_speech = models.ForeignKey(PartOfSpeech,on_delete="cascade")    
    language = models.ForeignKey(lang_models.Language,on_delete="cascade")    
    inflections = models.ManyToManyField("Inflection",blank=True)

class Inflection(models.Model):
    dict_entry = models.BooleanField(default=False)
    regsub = models.ForeignKey(RegexpReplacement,on_delete="cascade")    
    description_obj = models.ForeignKey(base_models.Description,on_delete="cascade")    

    @cached_property
    def description(self):
        return self.description_obj.build()

    def __str__(self):
        if not self.dict_entry:
            return "%s [%s]" % (self.regsub,self.description)
        return "%s [%s] [DICT]" % (self.regsub,self.description)
        

    def serialize(self):
        return {
            "dict_entry": self.dict_entry,
            "regsub": self.regsub.serialize(),
            "description": self.description_obj.name
        }

class Root(models.Model):
    root=models.CharField(max_length=1024)
    language = models.ForeignKey(lang_models.Language,on_delete="cascade")    
    tema_obj = models.ForeignKey(Tema,on_delete="cascade")    
    part_of_speech = models.ForeignKey(PartOfSpeech,on_delete="cascade")    
    description_obj = models.ForeignKey(base_models.Description,on_delete="cascade")    

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
    
class Derivation(base_models.AbstractName):
    language = models.ForeignKey(lang_models.Language,on_delete="cascade")    
    regsub = models.ForeignKey(RegexpReplacement,on_delete="cascade")    
    tema_obj = models.ForeignKey(Tema,on_delete="cascade")    
    description_obj = models.ForeignKey(base_models.Description,on_delete="cascade")    
    root_description_obj = models.ForeignKey(base_models.Description,
                                         on_delete="cascade",
                                         related_name="root_derivation_set")    
    root_part_of_speech = models.ForeignKey(PartOfSpeech,on_delete="cascade")    
    paradigma = models.ForeignKey(Paradigma,on_delete="cascade")    

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
    def root_description(self):
        return self.root_description_obj.build()

    @cached_property
    def tema(self):
        return self.tema_obj.build()

    def clean(self):
        if self.language != self.paradigma.language:
            raise ValidationError(_('Paradigma and language are not compatible.'))

#class ParadigmaInflection(models.Model):
#    paradigma = models.ForeignKey(Paradigma,on_delete="cascade")    
#    inflection = models.ForeignKey(Inflection,on_delete="cascade")    
    
class Fusion(base_models.AbstractName):
    language = models.ForeignKey(lang_models.Language,on_delete="cascade")    

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

class FusionRuleRelation(models.Model):
    fusion = models.ForeignKey(Fusion,on_delete="cascade")    
    fusion_rule = models.ForeignKey(FusionRule,on_delete="cascade")    
    order = models.IntegerField()

    class Meta:
        ordering = [ "order" ]

class Stem(models.Model):
    root = models.ForeignKey(Root,on_delete="cascade")    
    derivation = models.ForeignKey(Derivation,on_delete="cascade")    

    def __str__(self): return self.stem

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

    @cached_property
    def description(self):
        ddesc=self.derivation.description
        rdesc=self.root.description
        return ddesc+rdesc

    @cached_property
    def stem(self): return self.derivation.regsub.apply(self.root.root)

    @cached_property
    def tema(self): return self.root.tema

    @cached_property
    def paradigma(self): return self.derivation.paradigma

    @cached_property
    def language(self): return self.derivation.language

    @cached_property
    def part_of_speech(self): return self.derivation.paradigma.part_of_speech
    

class Word(models.Model):
    stem = models.ForeignKey(Stem,on_delete="cascade")    
    inflection = models.ForeignKey(Inflection,on_delete="cascade")    
    cache=models.CharField(max_length=1024,db_index=True,editable=False)

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
            return str(e)

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

class FusedWord(models.Model):
    fusion = models.ForeignKey(Fusion,on_delete="cascade")    
    cache = models.CharField(max_length=1024,db_index=True,editable=False)

    def clean(self):
        S=""
        n=0
        for word in [ rel.word for rel in self.fusedwordrelation_set.all() ]:
            rule=self.rules[n]
            print("   ",word,rule)
            S+=rule.regsub.apply(word.cache)
            n+=1
        self.cache=S

    def __str__(self): return self.cache

    @cached_property
    def rules(self):
        return [ rel.fusion_rule for rel in self.fusion.fusionrulerelation_set.all() ]

    @cached_property
    def words(self):
        return [ rel.word for rel in self.fusedwordrelation_set.all() ]
        
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
