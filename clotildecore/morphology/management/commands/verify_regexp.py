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
        re_list=models.RegexpReplacement.objects.all()

        for r in re_list:
            t=r.num_inflections+r.num_derivations+r.num_fusion_rules
            if t!=0: continue
            print("%10s => %10s %3d %3d %3d" % (r.pattern,r.replacement,r.num_inflections,
                                                r.num_derivations,r.num_fusion_rules))
                
