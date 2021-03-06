#! /usr/bin/python
# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand

from morphology import models
from languages import models as lang_models

class Command(BaseCommand):
    requires_migrations_checks = True
    help = 'Rebuild derived tables for language <name>'

    def add_arguments(self, parser):
        parser.add_argument(
            'name',
            help='name of language',
        )
        parser.add_argument(
            '--fusion',
            help='name of language',
            type=int,
            nargs='+'
        )

    def handle(self, *args, **options):
        language_name = options["name"]
        fusion_ids=options["fusion"]
        language=lang_models.Language.objects.get(name=language_name)
        if fusion_ids:
            fusion_list=models.Fusion.objects.filter(language=language,pk__in=fusion_ids)
        else:
            fusion_list=models.Fusion.objects.filter(language=language)
        models.FusedWord.objects.rebuild(language,fusion_list)
