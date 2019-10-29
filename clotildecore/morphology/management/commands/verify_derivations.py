#! /usr/bin/python
# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand

from morphology import models
from languages import models as lang_models

class Command(BaseCommand):
    requires_migrations_checks = True
    help = 'Verify derivations for language <name>'

    def add_arguments(self, parser):
        parser.add_argument(
            'language',
            help='name of language',
        )

    def handle(self, *args, **options):
        language_name = options["language"]
        language=lang_models.Language.objects.get(name=language_name)
        der_list=[ {
            "name": d.name,
            "regsub": (d.regsub.pattern,d.regsub.replacement),
            "paradigma": d.paradigma.name,
            "id": d.id,
            "root_part_of_speech": d.root_part_of_speech.name,
            "part_of_speech": d.part_of_speech.name,
            "description": d.description,
            "tema": d.tema
        } for d in  models.Derivation.objects.filter(language=language) ]

        der_list=list( models.Derivation.objects.filter(language=language) )

        n=-1
        for d1 in der_list:
            n+=1
            for d2 in der_list[n+1:]:
                if d1.regsub.pattern!=d2.regsub.pattern: continue
                if d1.regsub.replacement!=d2.regsub.replacement: continue
                if d1.root_part_of_speech.pk!=d2.root_part_of_speech.pk: continue
                if d1.paradigma.pk!=d2.paradigma.pk: continue
                if d1.description!=d2.description: continue

                print("==",d1.num_stem,d1,"|",d1.tema_obj)
                print("    ",d2.num_stem,d2,"|",d2.tema_obj)

                
                
