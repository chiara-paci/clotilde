#! /usr/bin/python
# -*- coding: utf-8 -*-

import re,time
import tarfile,json,io
import os,pwd,grp

from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist

from languages import models

def build_tarinfo(fname,data):
    data = data.encode('utf8')
    info = tarfile.TarInfo(name=fname)
    info.size = len(data)
    info.uid=os.getuid()
    info.gid=os.getgid()
    info.mode=0o644
    info.uname=pwd.getpwuid(os.getuid())[0] 
    info.gname=grp.getgrgid(os.getgid())[0]
    info.mtime=time.time()
    return info, io.BytesIO(data)

class Command(BaseCommand):
    requires_migrations_checks = True
    help = 'Export language <name> to file <fname.lar>'

    def add_arguments(self, parser):
        parser.add_argument(
            'name',
            help='name of language',
        )
        parser.add_argument(
            'fname',
            help='filename',
        )

    def handle(self, *args, **options):
        name = options["name"]
        fname = options["fname"]

        language=models.Language.objects.get(name=name)
        archive=tarfile.open(name=fname,mode="w:bz2")

        D=language.serialize()
        info,bdata=build_tarinfo("./index.json",json.dumps(D))
        archive.addfile(info, bdata)

        non_words={ w.name: w.word for w in models.NonWord.objects.filter(language=language) }
        info,bdata=build_tarinfo("./non_words.json",json.dumps(non_words))
        archive.addfile(info, bdata)
        

        archive.close()
