#! /usr/bin/python
# -*- coding: utf-8 -*-

import re,time
import tarfile,json,io
import os,pwd,grp

from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist

from morphology import models
from languages import models as lang_models

def combine(list_of_list):
    if len(list_of_list)==0: return []
    if len(list_of_list)==1: 
        return [ [x] for x in list_of_list[0] ]
    A=list_of_list[0]
    B=combine(list_of_list[1:])
    ret=[]
    for x in A:
        for y in B:
            ret.append( [x]+y )
    return ret

class Command(BaseCommand):
    requires_migrations_checks = True
    help = 'Rebuild derived tables for language <name>'

    def add_arguments(self, parser):
        parser.add_argument(
            'name',
            help='name of language',
        )

    def handle(self, *args, **options):
        language_name = options["name"]
        language=lang_models.Language.objects.get(name=language_name)

        models.FusedWordRelation.objects.filter(fused_word__fusion__language=language).delete()
        models.FusedWord.objects.filter(fusion__language=language).delete()

        # phase 1. stems
        root_list=models.Root.objects.filter(language=language)
        der_list=models.Derivation.objects.filter(language=language)
        ok=[]
        for root in root_list:
            for der in der_list:
                if root.part_of_speech != der.root_part_of_speech: continue
                if not (der.tema <= root.tema): continue
                if not (der.root_description <= root.description): continue
                stem,created=models.Stem.objects.get_or_create(root=root,derivation=der)
                print("S",stem)
                ok.append(stem.pk)
        models.Word.objects.exclude(stem__pk__in=ok).filter(stem__root__language=language).delete()
        models.Stem.objects.exclude(pk__in=ok).filter(root__language=language).delete()

 
        # phase 2. words
        stem_list=models.Stem.objects.filter(root__language=language)
        par_list=models.Paradigma.objects.filter(language=language)
 
        ok=[]
        for stem in stem_list:
            for infl in stem.paradigma.inflections.all():
                word,created=models.Word.objects.get_or_create(stem=stem,inflection=infl)
                word.clean()
                word.save()
                print("W",word)
                ok.append(word.pk)
        models.Word.objects.exclude(pk__in=ok).filter(stem__root__language=language).delete()

        # phase 3. fused words

        models.FusedWord.objects.rebuild(language)
