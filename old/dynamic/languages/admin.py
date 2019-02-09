from django.contrib import admin
from languages.models import *

class LanguageAdmin(admin.ModelAdmin):
    list_display=['name','has_case','case_set','token_regexp_set','token_regexp_expression']
    list_editable=['case_set','token_regexp_set']

admin.site.register(Language,LanguageAdmin)
