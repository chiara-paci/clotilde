from django.contrib import admin
from . import models

class CorpusAdmin(admin.ModelAdmin):
    list_display=['name','description']

admin.site.register(models.Author)
admin.site.register(models.Corpus,CorpusAdmin)


class TextAdmin(admin.ModelAdmin):
    list_display=['title','author','corpus']
    list_filter=["corpus"]
admin.site.register(models.Text,TextAdmin)

admin.site.register(models.WDConcorso)
admin.site.register(models.WDForum)
admin.site.register(models.WDAuthor)

class WDTextAdmin(admin.ModelAdmin):
    list_display=['title','author','pub_date','forum','get_wd_url']

admin.site.register(models.WDText,WDTextAdmin)

