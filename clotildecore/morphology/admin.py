from django.contrib import admin

from . import models

admin.site.register(models.RegexpReplacement)
admin.site.register(models.TemaArgument)
admin.site.register(models.TemaValue)
admin.site.register(models.TemaEntry)
admin.site.register(models.FusionRuleRelation)

class TemaEntryInline(admin.TabularInline):
    model = models.TemaEntry
    extra = 0

class TemaAdmin(admin.ModelAdmin):
    inlines=[TemaEntryInline]

admin.site.register(models.Tema,TemaAdmin)

class StemAdmin(admin.ModelAdmin):
    list_display=["stem","part_of_speech","root","derivation","tema","paradigma"]

admin.site.register(models.Stem,StemAdmin)

class ParadigmaInflectionInline(admin.TabularInline):
    model = models.Paradigma.inflections.through
    extra = 0

class ParadigmaAdmin(admin.ModelAdmin):
    inlines=[ParadigmaInflectionInline]
    exclude=["inflections"]
    save_as=True

admin.site.register(models.Paradigma,ParadigmaAdmin)

class PartOfSpeechAdmin(admin.ModelAdmin):
    list_display=[ "name","bg_color","fg_color" ]
    list_editable=[ "bg_color","fg_color" ]

admin.site.register(models.PartOfSpeech,PartOfSpeechAdmin)

class WordAdmin(admin.ModelAdmin):
    list_display=["cache","dict_entry","part_of_speech","stem","tema","paradigma","description"]
    
admin.site.register(models.Word,WordAdmin)

class InflectionAdmin(admin.ModelAdmin):
    list_filter=["paradigma","description_obj"]
    list_display=["regsub","description","description_obj"]
    inlines=[ParadigmaInflectionInline]
    save_as=True

admin.site.register(models.Inflection,InflectionAdmin)

class DerivationAdmin(admin.ModelAdmin):
    save_as=True

admin.site.register(models.Derivation,DerivationAdmin)

class RootAdmin(admin.ModelAdmin):
    save_as=True
    list_filter=["part_of_speech"]
    list_display=["root","language","part_of_speech","tema","description"]

admin.site.register(models.Root,RootAdmin)

class FusionRuleRelationInline(admin.TabularInline):
    model = models.FusionRuleRelation
    extra = 0

class FusionAdmin(admin.ModelAdmin): 
    inlines=[FusionRuleRelationInline]

admin.site.register(models.Fusion,FusionAdmin)

class FusionRuleAdmin(admin.ModelAdmin): 
    inlines=[FusionRuleRelationInline]
    save_as=True

admin.site.register(models.FusionRule,FusionRuleAdmin)


class FusedWordRelationInline(admin.TabularInline):
    model = models.FusedWordRelation
    extra = 0

class FusedWordAdmin(admin.ModelAdmin):
    list_display = [ "cache", "fusion" ]
    inlines = [FusedWordRelationInline]

admin.site.register(models.FusedWord,FusedWordAdmin)
admin.site.register(models.FusedWordRelation)
