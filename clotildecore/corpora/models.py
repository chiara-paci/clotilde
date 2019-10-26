from django.db import models
from django.conf import settings
from django.db.models.functions import Length
from django.utils.text import slugify

# Create your models here.

from languages import models as lang_models
from base import models as base_models

class Author(models.Model):
    name = models.CharField(max_length=1024,db_index=True)

    def __str__(self): return(self.name)

    def serialize(self):
        return str(self.name)

class Corpus(base_models.AbstractNameDesc):
    language = models.ForeignKey('languages.Language',on_delete="cascade")

    def get_absolute_url(self):
        return "/%s/corpus/%d" % ("corpora",self.id)

    class Meta:
        verbose_name_plural = 'corpora'

    def text_ordered_by_len(self):
        return self.text_set.all().annotate(text_len=Length("text")).order_by("text_len")

    def serialize(self):
        ret={
            "name": self.name,
            "description": self.description,
            "language": str(self.language.name),
            "texts": []
        }
        for t in self.text_set.all():
            ret["texts"].append(t.serialize())
        return ret

class TextManager(models.Manager):
    def all_ordered_by_len(self):
        return self.all().annotate(text_len=Length("text")).order_by("text_len")

class Text(models.Model):
    corpus = models.ForeignKey(Corpus,on_delete="cascade")
    author = models.ForeignKey(Author,on_delete="cascade")
    title = models.CharField(max_length=1024)
    text = models.TextField()
    label = models.SlugField(max_length=128)

    class Meta:
        unique_together = [ ["corpus","label"] ]
    
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

    def save(self,*args,**kwargs):
        if not self.label:
            self.label=slugify(self.title)[:128]
        models.Model.save(self,*args,**kwargs)

    def serialize(self):
        ret={
            "author": self.author.serialize(),
            "title": self.title,
            "file_name": "%s.txt" % self.label,
            "metadata": []
        }
        for m in self.metadataentry_set.all():
            ret["metadata"].append( [str(m.argument),str(m.value)] )
        return ret

class MetaDataArgument(base_models.AbstractName): pass

class MetaDataEntry(models.Model):
    text = models.ForeignKey(Text,on_delete="cascade")    
    argument = models.ForeignKey(MetaDataArgument,on_delete="cascade")    
    value = models.TextField()

    def __str__(self):
        return "%s=%s" % (str(self.argument),str(self.value))

    class Meta:
        ordering=["argument","value"]
    
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
    pub_date = models.DateTimeField(auto_now_add=False)

    def __str__(self): return(str(self.text))
    
    def get_absolute_url(self):
        return self.text.get_absolute_url()

    def get_wd_url(self):
        lab=self.title.lower().replace(" ","-")
        return "http://www.writersdream.org/forum/topic/%d-%s" % (self.wd_id,lab)

    def get_wd_tag(self): return(self.concorso.tag)


