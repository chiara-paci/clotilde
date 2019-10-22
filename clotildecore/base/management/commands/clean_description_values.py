#! /usr/bin/python
# -*- coding: utf-8 -*-

import re,time

from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist

from base import models


class Command(BaseCommand):
    requires_migrations_checks = True
    help = 'Export <language>'

    def add_arguments(self, parser):
        parser.add_argument(
            'language',
            help='Language file',
        )

    def handle(self, *args, **options):
        for e in models.Entry.objects.all():
            if e.value.string.startswith('['):
                t=e.value.string.replace('[','').replace(']','').split(',')
                s=t[0].replace("'","")
                if t[1]=="True":
                    e.invert=True
                else:
                    e.invert=False
                e.value.string=s
                e.value.save()
                e.save()


