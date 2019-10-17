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
            "tema": d.tema
        } for d in  models.Derivation.objects.filter(language=language) ]


        duplicates=[]
        for d1 in der_list:
            for d2 in der_list:
                if d1["id"]==d2["id"]: continue
                if d1["root_part_of_speech"]!=d2["root_part_of_speech"]: continue
                if d1["part_of_speech"]!=d2["part_of_speech"]: continue
                if d1["tema"]==d2["tema"]:
                    duplicates.append( (d1,d2) )
                    print("==",d1,d2)
                
                
