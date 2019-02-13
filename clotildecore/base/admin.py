from django.contrib import admin
from . import models

admin.site.register(models.CasePair)

class CasePairInline(admin.TabularInline):
    model = models.CaseSet.pairs.through
    extra = 0

class CaseSetAdmin(admin.ModelAdmin):
    list_display=['name','length']
    inlines=[CasePairInline]
    fields=['name']

admin.site.register(models.CaseSet,CaseSetAdmin)

class TokenRegexpAdmin(admin.ModelAdmin):
    list_display=['name','regexp',"set_number"]
    list_editable=['regexp']

admin.site.register(models.TokenRegexp,TokenRegexpAdmin)

class AlphabeticOrderAdmin(admin.ModelAdmin):
    list_display=['name','order']
    list_editable=['order']

admin.site.register(models.AlphabeticOrder,AlphabeticOrderAdmin)

class TokenRegexpSetThroughAdmin(admin.ModelAdmin):
    list_display=['__str__','token_regexp_set','order','token_regexp','regexp','bg_color','fg_color','disabled']
    list_editable=['order','token_regexp','bg_color','fg_color','disabled']

    list_filter=["token_regexp_set"]

admin.site.register(models.TokenRegexpSetThrough,TokenRegexpSetThroughAdmin)

class TokenRegexpInline(admin.TabularInline):
    model = models.TokenRegexpSet.regexps.through
    extra = 0

class TokenRegexpSetAdmin(admin.ModelAdmin):
    list_display=['name','regexp_all']
    inlines = [TokenRegexpInline]

admin.site.register(models.TokenRegexpSet,TokenRegexpSetAdmin)

class LanguageAdmin(admin.ModelAdmin):
    list_display=['name','has_case','case_set','token_regexp_set','token_regexp_expression']
    list_editable=['case_set','token_regexp_set']

admin.site.register(models.Language,LanguageAdmin)

class NotWordAdmin(admin.ModelAdmin):
    list_display=('name','word')

admin.site.register(models.NotWord,NotWordAdmin)
