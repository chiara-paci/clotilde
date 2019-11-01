#! /usr/bin/python
# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand

from morphology import models

class Command(BaseCommand):
    requires_migrations_checks = True
    help = 'Verify temas for language <name>'

    def handle(self, *args, **options):
        seq=[]
        for x in models.TemaEntry.objects.all().values("argument__name","value__name").distinct():
            arg=x["argument__name"]
            val=x["value__name"]
            obj=models.TemaEntry.objects.filter(argument__name=arg,value__name=val).order_by("id").first()
            seq.append( (arg,val,obj) )
        for arg,val,obj in seq:
            for rel in models.TemaEntryRelation.objects.filter(entry__argument__name=arg,entry__value__name=val):
                rel.entry=obj
                rel.save()
                print( "%20s %20s %s" % (arg,val,rel) )
        
            
