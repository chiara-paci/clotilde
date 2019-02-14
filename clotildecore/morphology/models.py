from django.db import models

# Create your models here.

from base import models as base_models
from languages import models as lang_models

class RegexpReplacement(models.Model):
    pattern=models.CharField(max_length=1024)
    replacement=models.CharField(max_length=1024)

class PartOfSpeech(base_models.AbstractName): pass

class Tema(base_models.AbstractName): pass
class TemaArgument(base_models.AbstractName): pass
class TemaValue(base_models.AbstractName): pass

class TemaEntry(models.Model):
    tema = models.ForeignKey(Tema,on_delete="cascade")    
    argument = models.ForeignKey(TemaArgument,on_delete="cascade")    
    value = models.ForeignKey(TemaValue,on_delete="cascade")    

class Paradigma(base_models.AbstractName):
    part_of_speech = models.ForeignKey(PartOfSpeech,on_delete="cascade")    
    language = models.ForeignKey(lang_models.Language,on_delete="cascade")    

class Root(models.Model):
    root=models.CharField(max_length=1024)
    language = models.ForeignKey(lang_models.Language,on_delete="cascade")    
    tema = models.ForeignKey(Tema,on_delete="cascade")    
    part_of_speech = models.ForeignKey(PartOfSpeech,on_delete="cascade")    
    description = models.ForeignKey(base_models.Description,on_delete="cascade")    
    
class Derivation(base_models.AbstractName):
    regsub = models.ForeignKey(RegexpReplacement,on_delete="cascade")    
    tema = models.ForeignKey(Tema,on_delete="cascade")    
    description = models.ForeignKey(base_models.Description,on_delete="cascade")    
    root_description = models.ForeignKey(base_models.Description,
                                         on_delete="cascade",
                                         related_name="root_derivation_set")    
    root_part_of_speech = models.ForeignKey(PartOfSpeech,on_delete="cascade")    
    paradigma = models.ForeignKey(Paradigma,on_delete="cascade")    

class Inflection(models.Model):
    dict_entry = models.BooleanField(default=False)
    regsub = models.ForeignKey(RegexpReplacement,on_delete="cascade")    
    description = models.ForeignKey(base_models.Description,on_delete="cascade")    

class ParadigmaInflection(models.Model):
    paradigma = models.ForeignKey(Paradigma,on_delete="cascade")    
    inflection = models.ForeignKey(Inflection,on_delete="cascade")    
    
class Fusion(base_models.AbstractName):
    language = models.ForeignKey(lang_models.Language,on_delete="cascade")    

class FusionRule(base_models.AbstractName):
    regsub = models.ForeignKey(RegexpReplacement,on_delete="cascade")    
    tema = models.ForeignKey(Tema,on_delete="cascade")    
    part_of_speech = models.ForeignKey(PartOfSpeech,on_delete="cascade")    
    description = models.ForeignKey(base_models.Description,on_delete="cascade")    

class FusionRuleRelation(models.Model):
    fusion = models.ForeignKey(Fusion,on_delete="cascade")    
    fusion_rule = models.ForeignKey(FusionRule,on_delete="cascade")    
    order = models.IntegerField()

class Stem(models.Model):
    root = models.ForeignKey(Root,on_delete="cascade")    
    derivation = models.ForeignKey(Derivation,on_delete="cascade")    

class Word(models.Model):
    stem = models.ForeignKey(Stem,on_delete="cascade")    
    inflection = models.ForeignKey(Inflection,on_delete="cascade")    
    cache=models.CharField(max_length=1024,db_index=True,editable=False)
    cache_description=models.CharField(max_length=8000,editable=False)
    cache_part_of_speech=models.CharField(max_length=1024,db_index=True,editable=False)

    def save(self,*args,**kwargs):
        models.Model.save(self,*args,**kwargs)

class FusedWord(models.Model):
    fusion = models.ForeignKey(Fusion,on_delete="cascade")    
    cache = models.CharField(max_length=1024,db_index=True,editable=False)
    
    def save(self,*args,**kwargs):
        models.Model.save(self,*args,**kwargs)

class FusionWordRelation(models.Model):
    fused_word = models.ForeignKey(FusedWord,on_delete="cascade")    
    word = models.ForeignKey(Word,on_delete="cascade")    
    order = models.IntegerField()

