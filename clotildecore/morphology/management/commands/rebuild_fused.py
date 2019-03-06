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

    def handle(self, *args, **options):
        language_name = options["name"]
        language=lang_models.Language.objects.get(name=language_name)
        models.FusedWord.objects.rebuild(language)
