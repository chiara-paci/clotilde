from django.contrib import admin

from . import models

admin.site.register(models.RegexpReplacement)
admin.site.register(models.TemaArgument)
admin.site.register(models.TemaValue)
admin.site.register(models.TemaEntry)
admin.site.register(models.Root)
admin.site.register(models.Derivation)
admin.site.register(models.Inflection)
admin.site.register(models.Fusion)
admin.site.register(models.FusionRule)
admin.site.register(models.FusionRuleRelation)
admin.site.register(models.FusedWord)
admin.site.register(models.FusionWordRelation)

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
    pass

admin.site.register(models.Paradigma,ParadigmaAdmin)

class PartOfSpeechAdmin(admin.ModelAdmin):
    list_display=[ "name","bg_color","fg_color" ]
    list_editable=[ "bg_color","fg_color" ]

admin.site.register(models.PartOfSpeech,PartOfSpeechAdmin)


class WordAdmin(admin.ModelAdmin):
    list_display=["cache","part_of_speech","stem","tema","paradigma","description"]
    

admin.site.register(models.Word,WordAdmin)
