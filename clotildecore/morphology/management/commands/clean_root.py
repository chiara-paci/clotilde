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
            'language',
            help='name of language',
        )
        parser.add_argument(
            'root',
            help='root',
            nargs='+'
        )

    def handle(self, *args, **options):
        language_name = options["language"]
        root_list = options["root"]
        language=lang_models.Language.objects.get(name=language_name)
        models.Root.objects.clean_derived_tables(language,root_names=root_list)
