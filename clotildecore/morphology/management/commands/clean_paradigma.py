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
        parser.add_argument(
            'paradigma_list',
            help='name of language',
            type=int,
            nargs='+'
        )

        
    def handle(self, *args, **options):
        language_name = options["language"]
        language=lang_models.Language.objects.get(name=language_name)

        qset=models.Paradigma.objects.filter(pk__in=options["paradigma_list"])

        for par in qset:
            print("%-40.40s %3d" % (par.name,par.count_derivations))
            if par.count_derivations>0:
                for d in par.derivation_set.all():
                    print("    ",d)
                continue
            par.inflections.clear()
            par.delete()
