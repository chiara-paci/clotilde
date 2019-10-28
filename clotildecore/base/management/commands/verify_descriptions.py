#! /usr/bin/python
# -*- coding: utf-8 -*-

import re,time

from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist

from base import models


class Command(BaseCommand):
    requires_migrations_checks = True
    help = 'Export <language>'

    # def add_arguments(self, parser):
    #     parser.add_argument(
    #         'language',
    #         help='Language file',
    #     )

    def handle(self, *args, **options):
        desc_list=list(models.Description.objects.all())

        n=-1
        for d1 in desc_list:
            n+=1
            b1=d1.build()
            for d2 in desc_list[n+1:]:
                b2=d2.build()
                if b1==b2:
                    print("==", d1,d1.count_references)
                    print("    ",d2,d2.count_references)
                    print("     b1=",b1)
                    print("     b2=",b2)
