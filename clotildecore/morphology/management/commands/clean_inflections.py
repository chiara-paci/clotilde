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

        qset=models.Inflection.objects.all()

        for infl in qset:
            if infl.num_paradigmas == 0:
                print("%3d %s" % (infl.num_paradigmas,str(infl),))
                infl.delete()
