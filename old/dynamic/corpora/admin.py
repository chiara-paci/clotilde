from django.contrib import admin
from corpora.models import *

class CorpusAdmin(admin.ModelAdmin):
    list_display=['name','description']

admin.site.register(Author)
admin.site.register(Corpus,CorpusAdmin)


class TextAdmin(admin.ModelAdmin):
    list_display=['title','author','pub_date']
admin.site.register(Text,TextAdmin)

admin.site.register(WDConcorso)
admin.site.register(WDForum)
admin.site.register(WDAuthor)

class WDTextAdmin(admin.ModelAdmin):
    list_display=['title','author','pub_date','forum','get_wd_url']
admin.site.register(WDText,WDTextAdmin)

