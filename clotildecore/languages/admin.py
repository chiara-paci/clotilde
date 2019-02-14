from django.contrib import admin

# Register your models here.

from . import models

class LanguageAdmin(admin.ModelAdmin):
    list_display=['name','has_case','case_set','token_regexp_set','token_regexp_expression']
    list_editable=['case_set','token_regexp_set']

admin.site.register(models.Language,LanguageAdmin)

class NonWordAdmin(admin.ModelAdmin):
    list_display=('name','word')

admin.site.register(models.NonWord,NonWordAdmin)
