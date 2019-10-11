from django.contrib import admin
from django import forms
from django.db.models.query import QuerySet
from django.utils.html import format_html

from . import models

admin.site.register(models.TemaArgument)
admin.site.register(models.TemaValue)
admin.site.register(models.TemaEntry)
admin.site.register(models.FusionRuleRelation)

class RegexpReplacementAdmin(admin.ModelAdmin):
    list_display = [ "__str__", "pattern", "replacement" ]
    list_editable = [ "pattern", "replacement" ]
    list_filter = [ "pattern", "replacement" ]

admin.site.register(models.RegexpReplacement,RegexpReplacementAdmin)

class TemaEntryInline(admin.TabularInline):
    model = models.TemaEntry
    extra = 0

class DerivationInline(admin.TabularInline):
    model = models.Derivation
    extra = 0

    
class TemaAdmin(admin.ModelAdmin):
    inlines=[TemaEntryInline] #,DerivationInline]
    list_display=[ "name", "build", "num_roots","num_derivations","num_fusion_rules" ]
    save_as=True

admin.site.register(models.Tema,TemaAdmin)

class StemAdmin(admin.ModelAdmin):
    list_display=["stem","part_of_speech","root","derivation","tema","paradigma"]

admin.site.register(models.Stem,StemAdmin)

def build_static_iterator(obj_list):
    class ModelChoiceIterator:
        def __init__(self, field):
            self.field = field
            self._object_list=obj_list
            if self.field.empty_label is not None:
                self._ind=-2
            else:
                self._ind=-1

        def __next__(self):
            self._ind+=1
            if self._ind<0: return ("", self.field.empty_label)
            if self._ind >= len(self._object_list): raise StopIteration()
            return self.choice( self._object_list[self._ind] )

        def __iter__(self): return type(self)(self.field)

        def __len__(self):
            return len(self._object_list) + (1 if self.field.empty_label is not None else 0)

        def __bool__(self):
            return self.field.empty_label is not None or len(self._object_list)!=0

        def choice(self, obj):
            return (self.field.prepare_value(obj), self.field.label_from_instance(obj))

    return ModelChoiceIterator
        
class ParadigmaInflectionInline(admin.TabularInline):
    model = models.Paradigma.inflections.through
    extra = 0

    def __init__(self,*args,**kwargs):
        obj_list=list(models.Inflection.objects.all().select_related())
        self._inflection_iterator=build_static_iterator(obj_list)
        admin.TabularInline.__init__(self,*args,**kwargs)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        field=super().formfield_for_foreignkey(db_field, request, **kwargs)
        if db_field.name == "inflection":
            field.iterator=self._inflection_iterator
        return field

class ParadigmaAdmin(admin.ModelAdmin):
    list_display=["name","part_of_speech"]
    list_filter=["part_of_speech"]
    list_editable=["part_of_speech"]
    inlines=[ParadigmaInflectionInline]
    exclude=["inflections"]
    save_as=True

admin.site.register(models.Paradigma,ParadigmaAdmin)

class PartOfSpeechAdmin(admin.ModelAdmin):
    list_display=[ "name","example","bg_color","fg_color" ]
    list_editable=[ "bg_color","fg_color" ]

    def example(self,obj):
        return format_html('<span style="background-color:%s;color:%s">%s</span>' % (obj.bg_color,obj.fg_color,obj.name))
    #example.allow_tags = True

admin.site.register(models.PartOfSpeech,PartOfSpeechAdmin)

class WordAdmin(admin.ModelAdmin):
    list_display=["cache","dict_entry","part_of_speech","stem","tema","paradigma","description"]
    
admin.site.register(models.Word,WordAdmin)

class InflectionAdmin(admin.ModelAdmin):
    list_filter=["dict_entry","paradigma","description_obj"]
    list_display=["regsub","dict_entry","description","description_obj"]
    inlines=[ParadigmaInflectionInline]
    save_as=True

admin.site.register(models.Inflection,InflectionAdmin)

class DerivationAdmin(admin.ModelAdmin):
    list_display = [ "name", "tema", "root_part_of_speech", "root_description", 
                     "part_of_speech", "description", "regsub", "paradigma" ]
    list_filter = [ "root_part_of_speech"]
    list_editable = [ "root_part_of_speech" ]
    save_as=True

admin.site.register(models.Derivation,DerivationAdmin)

class RootAdmin(admin.ModelAdmin):
    save_as=True
    list_filter=["part_of_speech"]
    list_display=["root","language","part_of_speech","tema_obj","description_obj"]
    list_editable=["description_obj","tema_obj","part_of_speech"]

admin.site.register(models.Root,RootAdmin)

class FusionRuleRelationInline(admin.TabularInline):
    model = models.FusionRuleRelation
    extra = 0

class FusionAdmin(admin.ModelAdmin): 
    inlines=[FusionRuleRelationInline]
    save_as=True

admin.site.register(models.Fusion,FusionAdmin)

class FusionRuleAdmin(admin.ModelAdmin): 
    inlines=[FusionRuleRelationInline]
    save_as=True
    list_display=[ "name", "tema", "part_of_speech", "description", "regsub" ]

admin.site.register(models.FusionRule,FusionRuleAdmin)


class FusedWordRelationInline(admin.TabularInline):
    model = models.FusedWordRelation
    extra = 0

class FusedWordAdmin(admin.ModelAdmin):
    list_display = [ "cache", "fusion" ]
    inlines = [FusedWordRelationInline]

admin.site.register(models.FusedWord,FusedWordAdmin)
admin.site.register(models.FusedWordRelation)
