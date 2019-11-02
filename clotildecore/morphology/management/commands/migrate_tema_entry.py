#! /usr/bin/python
# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand

from morphology import models

class Command(BaseCommand):
    requires_migrations_checks = True
    help = 'Verify temas for language <name>'

    def handle(self, *args, **options):
        seq=[]
        for der in models.Derivation.objects.all():
            tentry=der.tema_obj.temaentryrelation_set.first().entry
            der.tema_entry=tentry
            der.save()
            print("%30s %s" % (str(tentry),str(der)) ) 
            
