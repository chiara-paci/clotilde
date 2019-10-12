from django.db import models
from django.db.models.signals import post_save
from django.utils.functional import cached_property

from base import tokens as base_tokens
from base import models as base_models
from morphology import models as morph_models
from morphology import tokens as morph_tokens
from . import tokens

# Create your models here.
class Language(base_models.AbstractName):
    token_regexp_set = models.ForeignKey(base_models.TokenRegexpSet,on_delete="cascade",related_name="a_set")
    case_set = models.ForeignKey(base_models.CaseSet,default=1,on_delete="cascade",related_name="b_set")
    period_sep = models.ForeignKey(base_models.TokenRegexp,on_delete="cascade",related_name="c_set")
    alphabetic_order = models.ForeignKey(base_models.AlphabeticOrder,on_delete="cascade",related_name="d_set")

    def clean(self):
        if not self.token_regexp_set.has_regexp(self.period_sep):
            raise ValidationError('Period regexp must be in language token regexp set')
        models.Model.clean(self)

    def __unicode__(self): return(self.name)

    def has_case(self):
        return(self.case_set.length()!=0)

    def alpha_tokenize(self,text):
        rexp_list,token_list=self.token_regexp_set.tokenize(text)
        style_list=[ (name+": "+rexp_t,label,bg,fg) for name,label,bg,fg,rexp,rexp_t,invariant in rexp_list ]
        style_list.append( ("not matched","not-found","#900000","#ffffff") )
        return style_list,token_list

    def morph_tokenize(self,text):
        #rexp_list,token_list=self.token_regexp_set.tokenize(text)
        style_list,token_list=self.alpha_tokenize(text)

        t_list=list(set([ t.text.lower() for t in filter(lambda x: isinstance(x,base_tokens.TokenBase),token_list) ]))

        non_words={}
        for w in NonWord.objects.filter(language=self,word__in=t_list):
            if w.word not in non_words: non_words[w.word]=[]
            non_words[w.word].append(w)

        words={}
        for w in morph_models.Word.objects.filter(stem__root__language=self,cache__in=t_list):
            if w.cache not in words: words[w.cache]=[]
            words[w.cache].append( ("word",w) )
        for w in morph_models.FusedWord.objects.filter(fusion__language=self,cache__in=t_list):
            if w.cache not in words: words[w.cache]=[]
            words[w.cache].append( ("fused_word",w) )

        morph_list=[]
        #style_list=[]
        for t in token_list:
            if not type(t) is base_tokens.TokenBase:
                morph_list.append(t)
                continue
            if t.invariant:
                morph_list.append(t)
                continue                
            if t.text.lower() in non_words: 
                morph_list.append( tokens.TokenNonWord(t) )
                continue
            if not t.text.lower() in words:
                morph_list.append(morph_tokens.TokenNotFoundMorph(t))
                continue
            s_list,token=morph_tokens.factory(t,words[t.text.lower()])
            style_list+=s_list
            morph_list.append(token)

        style_list.append( ("non word","non-word","#f0f0f0","#909090") )
        style_list.append( ("marker","marker","#e0e0e0","#909090") )
        style_list.append( ("not matched (alpha)","not-found","#900000","#ffffff") )
        style_list.append( ("not matched (morphology)","not-found-morph","#c00000","#ffffff") )
        style_list=list(set(style_list))
        return style_list,morph_list
        

    def token_regexp_expression(self):
        return(self.token_regexp_set.regexp_all())

    def get_absolute_url(self):
        return( "/languages/language/%d" % self.id )

    def part_of_speech_set(self):
        return(morph_models.PartOfSpeech.objects.by_language(self))

    def derivation_set(self):
        return(morph_models.Derivation.objects.by_language(self))

    def serialize(self):
        return { 
            "name": self.name,
            "alphabetic_order": self.alphabetic_order.serialize(),
            "token_regexp_set": self.token_regexp_set.serialize(),
            "case_set": self.case_set.serialize(),
            "period_sep": self.period_sep.name
        }

class NonWord(base_models.AbstractName):
    language = models.ForeignKey('Language',on_delete="cascade")    
    word=models.CharField(max_length=1024,db_index=True)

    def __unicode__(self): return("not word: "+self.name)

def insert_newlines_as_notword(sender,instance,created,**kwargs):
    for (r,n) in base_tokens.NEW_LINES: 
        NonWord.objects.get_or_create(language=instance,name="new line ("+r+")",word=n)

post_save.connect(insert_newlines_as_notword,sender=Language)
