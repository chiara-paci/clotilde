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
        models.FusedWord.objects.rebuild(language)
