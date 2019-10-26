#! /usr/bin/python
# -*- coding: utf-8 -*-

import re,time
import tarfile,json,io
import os,pwd,grp

from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist

from corpora import models
from languages import models as lang_models
from base import models as base_models
from base import functions

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
    help = 'Export corpus <name> to file <fname.lar>'

    def add_arguments(self, parser):
        parser.add_argument(
            'name',
            help='name of corpus',
        )
        parser.add_argument(
            'fname',
            help='filename',
        )

    def handle(self, *args, **options):
        name = options["name"]
        fname = options["fname"]

        corpus=models.Corpus.objects.get(name=name)
        archive=tarfile.open(name=fname,mode="w:bz2")

        ### base
        D=corpus.serialize()
        info,bdata=build_tarinfo("./index.json",json.dumps(D))
        archive.addfile(info, bdata)

        ### texts

        for t in corpus.text_set.all():
            info,bdata=build_tarinfo("./%s.txt" % t.label,t.text)
            archive.addfile(info,bdata)

        archive.close()
