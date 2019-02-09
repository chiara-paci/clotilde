from django.db import models
from django.conf import settings

# Create your models here.

from languages.models import Language
from base.models import AbstractNameDesc

class Author(models.Model):
    name = models.CharField(max_length=1024,db_index=True)

    def __unicode__(self): return(self.name)

class Corpus(AbstractNameDesc):
    language = models.ForeignKey(Language)
    def get_absolute_url(self):
        return "/%s/corpus/%d" % ("corpora",self.id)

    class Meta:
        verbose_name_plural = 'corpora'

class Text(models.Model):
    corpus = models.ForeignKey(Corpus)
    author = models.ForeignKey(Author)
    title = models.CharField(max_length=1024)
    text = models.TextField()
    pub_date = models.DateTimeField(auto_now_add=False)
    
    def __unicode__(self): return(self.title)

    def get_absolute_url(self):
        return "/%s/text/%d" % ("corpora",self.id)

    def length(self):
        L=len(self.text)
        return(L)

    def text_br(self):
        l=self.text.split('\n')
        t='[br/]'.join(l)
        return(t)

class WDConcorso(models.Model):
    title = models.CharField(max_length=1024)
    tag = models.CharField(max_length=10,db_index=True)

    def __unicode__(self): return("["+self.tag+"] "+self.title)

    class Meta:
        verbose_name_plural = 'Wd concorsi'

class WDForum(models.Model):
    title = models.CharField(max_length=1024)
    wd_id = models.IntegerField()

    def __unicode__(self): return(self.title)
    
class WDAuthor(Author):
    wd_id = models.IntegerField()

class WDText(Text):
    concorso = models.ForeignKey(WDConcorso)
    forum = models.ForeignKey(WDForum)
    wd_id = models.IntegerField()

    def __unicode__(self): return(unicode(self.text))
    
    def get_absolute_url(self):
        return self.text.get_absolute_url()

    def get_wd_url(self):
        lab=self.title.lower().replace(" ","-")
        return "http://www.writersdream.org/forum/topic/%d-%s" % (self.wd_id,lab)

    def get_wd_tag(self): return(self.concorso.tag)


