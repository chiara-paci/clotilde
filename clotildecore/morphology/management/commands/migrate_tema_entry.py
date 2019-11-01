#! /usr/bin/python
# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand

from morphology import models

class Command(BaseCommand):
    requires_migrations_checks = True
    help = 'Verify temas for language <name>'

    def handle(self, *args, **options):
        for entry in models.TemaEntry.objects.all():
            models.TemaEntryRelation.objects.get_or_create(tema=entry.tema,entry=entry)
