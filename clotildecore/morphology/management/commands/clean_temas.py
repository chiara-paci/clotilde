#! /usr/bin/python
# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand

from morphology import models
from languages import models as lang_models

class Command(BaseCommand):
    requires_migrations_checks = True
    help = 'Verify temas for language <name>'

    def add_arguments(self, parser):
        parser.add_argument(
            'language',
            help='name of language',
        )

    def handle(self, *args, **options):
        language_name = options["language"]
        language=lang_models.Language.objects.get(name=language_name)
        tema_list=list( models.Tema.objects.all() )

        duplicates=[]

        for t1 in tema_list:
            if t1.num_roots()!=0: continue
            if t1.num_derivations()!=0: continue
            if t1.num_fusion_rules()!=0: continue
            print(t1)

        
