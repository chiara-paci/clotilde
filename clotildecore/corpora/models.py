from django.db import models
from django.conf import settings

# Create your models here.

from base import models as base_models

class Author(models.Model):
    name = models.CharField(max_length=1024,db_index=True)

    def __str__(self): return(self.name)

class Corpus(base_models.AbstractNameDesc):
    language = models.ForeignKey(base_models.Language,on_delete="cascade")

    def get_absolute_url(self):
        return "/%s/corpus/%d" % ("corpora",self.id)

    class Meta:
        verbose_name_plural = 'corpora'

class Text(models.Model):
    corpus = models.ForeignKey(Corpus,on_delete="cascade")
    author = models.ForeignKey(Author,on_delete="cascade")
    title = models.CharField(max_length=1024)
    text = models.TextField()
    pub_date = models.DateTimeField(auto_now_add=False)
    
    def __str__(self): return(self.title)

    def get_absolute_url(self):
        return "/%s/text/%d" % ("corpora",self.id)

    def length(self):
        L=len(self.text)
        return(L)

    def html(self):
        html="\n".join(["<p>"+x+"</p>" for x in self.text.split('\n')])
        
        for k in ["center","left","right","i"]:
            html=html.replace('['+k+']','<'+k+'>')
            html=html.replace('[/'+k+']','</'+k+'>')
        return html

class WDConcorso(models.Model):
    title = models.CharField(max_length=1024)
    tag = models.CharField(max_length=10,db_index=True)

    def __str__(self): return("["+self.tag+"] "+self.title)

    class Meta:
        verbose_name_plural = 'Wd concorsi'

class WDForum(models.Model):
    title = models.CharField(max_length=1024)
    wd_id = models.IntegerField()

    def __str__(self): return(self.title)
    
class WDAuthor(Author):
    wd_id = models.IntegerField()

class WDText(Text):
    concorso = models.ForeignKey(WDConcorso,on_delete="cascade")
    forum = models.ForeignKey(WDForum,on_delete="cascade")
    wd_id = models.IntegerField()

    def __str__(self): return(str(self.text))
    
    def get_absolute_url(self):
        return self.text.get_absolute_url()

    def get_wd_url(self):
        lab=self.title.lower().replace(" ","-")
        return "http://www.writersdream.org/forum/topic/%d-%s" % (self.wd_id,lab)

    def get_wd_tag(self): return(self.concorso.tag)


