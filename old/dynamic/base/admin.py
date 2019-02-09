from django.contrib import admin
from base.models import *

admin.site.register(CasePair)
#admin.site.register(Classification)
#admin.site.register(CapitalizedWord)

# class ClassificationInline(admin.TabularInline):
#     model = Classification
#     extra = 0

# class CategoryAdmin(admin.ModelAdmin):
#     inlines = [ClassificationInline]

# admin.site.register(Category,CategoryAdmin)

# class PartOfSpeechAdmin(admin.ModelAdmin):
#     list_display=["name","is_inflected","bg_color","fg_color"]
#     list_editable=["bg_color","fg_color"]

# admin.site.register(PartOfSpeech,PartOfSpeechAdmin)

class CasePairInline(admin.TabularInline):
    model = CaseSet.pairs.through
    extra = 0

class CaseSetAdmin(admin.ModelAdmin):
    list_display=['name','length']
    inlines=[CasePairInline]
    fields=['name']

admin.site.register(CaseSet,CaseSetAdmin)

class TokenRegexpAdmin(admin.ModelAdmin):
    list_display=['name','regexp']
    list_editable=['regexp']

admin.site.register(TokenRegexp,TokenRegexpAdmin)

class AlphabeticOrderAdmin(admin.ModelAdmin):
    list_display=['name','order']
    list_editable=['order']

admin.site.register(AlphabeticOrder,AlphabeticOrderAdmin)

class TokenRegexpSetThroughAdmin(admin.ModelAdmin):
    list_display=['__unicode__','token_regexp_set','order','token_regexp','regexp','bg_color','fg_color','disabled']
    list_editable=['order','token_regexp','bg_color','fg_color','disabled']

admin.site.register(TokenRegexpSetThrough,TokenRegexpSetThroughAdmin)

class TokenRegexpInline(admin.TabularInline):
    model = TokenRegexpSet.regexps.through
    extra = 0

class TokenRegexpSetAdmin(admin.ModelAdmin):
    list_display=['name','regexp_all']
    inlines = [TokenRegexpInline]

admin.site.register(TokenRegexpSet,TokenRegexpSetAdmin)

