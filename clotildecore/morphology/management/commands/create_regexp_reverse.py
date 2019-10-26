#! /usr/bin/python
# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand

from morphology import models

class Command(BaseCommand):
    requires_migrations_checks = True
    help = 'Rebuild regexp reverse'

    def handle(self, *args, **options):
        models.RegexpReplacement.objects.update_reverse()

