from django.contrib import admin

# Register your models here.

from . import models

class NonWordInline(admin.TabularInline):
    model = models.NonWord
    extra = 0


class LanguageAdmin(admin.ModelAdmin):
    list_display=['name','has_case','case_set','token_regexp_set','token_regexp_expression']
    list_editable=['case_set','token_regexp_set']
    inlines=[NonWordInline]

admin.site.register(models.Language,LanguageAdmin)

class NonWordAdmin(admin.ModelAdmin):
    list_display=('name','word')

admin.site.register(models.NonWord,NonWordAdmin)
