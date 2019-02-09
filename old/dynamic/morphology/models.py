from django.db import models

from base.models import AbstractName
# Create your models here.

class NotWord(AbstractName):
    language = models.ForeignKey('languages.Language')    
    word=models.CharField(max_length=1024,db_index=True)

    def __unicode__(self): return("not word: "+self.name)
