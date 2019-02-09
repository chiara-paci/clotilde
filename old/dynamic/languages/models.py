# -*- coding: utf-8 -*-

from django.db import models
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save

from base.models import AbstractName,TokenRegexpSet,CaseSet,TokenRegexp,AlphabeticOrder,NEW_LINES
from morphology.models import NotWord

# Create your models here.


class Language(AbstractName):
    token_regexp_set = models.ForeignKey(TokenRegexpSet)
    case_set = models.ForeignKey(CaseSet,default=1)
    period_sep = models.ForeignKey(TokenRegexp)
    alphabetic_order = models.ForeignKey(AlphabeticOrder)

    def clean(self):
        if not self.token_regexp_set.has_regexp(self.period_sep):
            raise ValidationError('Period regexp must be in language token regexp set')
        models.Model.clean(self)

    def __unicode__(self): return(self.name)

    def has_case(self):
        return(self.case_set.length()!=0)

    def token_regexp_expression(self):
        return(self.token_regexp_set.regexp_all())


    def get_absolute_url(self):
        return( "/languages/language/%d" % self.id )

    def part_of_speech_set(self):
        return(PartOfSpeech.objects.by_language(self))

    def derivation_set(self):
        return(Derivation.objects.by_language(self))

def insert_newlines_as_notword(sender,instance,created,**kwargs):
    for (r,n) in NEW_LINES: 
        NotWord.objects.get_or_create(language=instance,name="new line ("+r+")",word=n)

post_save.connect(insert_newlines_as_notword,sender=Language)
