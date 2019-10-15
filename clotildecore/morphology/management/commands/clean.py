#! /usr/bin/python
# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand

from morphology import models
from languages import models as lang_models
from base import models as base_models


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

        for infl in models.Inflection.objects.all():
            n=infl.paradigma_set.count()
            if not n:
                print(infl,n)
                infl.delete()

        for reg in models.RegexpReplacement.objects.all():
            n_der=reg.derivation_set.count()
            n_infl=reg.inflection_set.count()
            n_frule=reg.fusionrule_set.count()

            if not n_infl+n_der+n_frule:
                #print(reg,n_infl,n_der,n_frule)
                reg.delete()
            print(reg,n_infl,n_der,n_frule)
