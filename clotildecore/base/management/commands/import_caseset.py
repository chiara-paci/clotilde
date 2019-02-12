#! /usr/bin/python
# -*- coding: utf-8 -*-

import re,time

from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist

from base import models

class Command(BaseCommand):
    requires_migrations_checks = True
    help = 'Import case set <name> from file <pairs>'

    def add_arguments(self, parser):
        parser.add_argument(
            'name',
            help='name of caseset',
        )
        parser.add_argument(
            'pairs',
            help='file of colon separated pairs',
        )

    def handle(self, *args, **options):
        name = options["name"]
        fname = options["pairs"]

        case_set,created=models.CaseSet.objects.get_or_create(name=name)

        #fname=args[0]
        with open(fname,'r') as fd:
            for r in fd.readlines():
                r=r.strip()
                if not r: continue
                if r.startswith('#'): continue
                t=r.split(":")
                if len(t)<2: continue
                case_pair,created=models.CasePair.objects.get_or_create(lower=t[0],upper=t[1])
                case_set.pairs.add(case_pair)
