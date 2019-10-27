#! /usr/bin/python
# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand

from morphology import models
from languages import models as lang_models

class Command(BaseCommand):
    requires_migrations_checks = True
    help = 'Verify temas for language <name>'

    def add_arguments(self, parser):
        parser.add_argument(
            'paradigma',
            help='paradigma',
            type=int,
            nargs=2
        )

    def handle(self, *args, **options):
        [par1,par2]=list(models.Paradigma.objects.filter(pk__in=options["paradigma"]))

        if par1.language!=par2.language:
            print("LANG %s != %s" % (par1.language,par2.language) )
            return

        if par1.part_of_speech!=par2.part_of_speech:
            print("POS  %s != %s" % (par1.part_of_speech,par2.part_of_speech) )
            return

        infl_list1=list(par1.inflections.order_by("pk"))
        infl_list2=list(par2.inflections.order_by("pk"))

        N=max(len(infl_list1),len(infl_list2))
        for n in range(0,N):
            if n>=len(infl_list1):
                print("NN")
                print("    ",infl_list2[n])
                continue
            if n>=len(infl_list2):
                print("NN",infl_list1[n])
                print("     -")
                continue
            if infl_list1[n].pk==infl_list2[n].pk: 
                print("==",infl_list1[n])
                print("    ",infl_list2[n])
                continue
            print("NN",infl_list1[n])
            print("    ",infl_list2[n])
