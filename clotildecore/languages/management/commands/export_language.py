#! /usr/bin/python
# -*- coding: utf-8 -*-

import re,time
import tarfile,json,io
import os,pwd,grp

from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist

from languages import models
from morphology import models as morph_models

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

        ### base
        D=language.serialize()
        info,bdata=build_tarinfo("./index.json",json.dumps(D))
        archive.addfile(info, bdata)

        ### non words
        non_words={ w.name: w.word for w in models.NonWord.objects.filter(language=language) }
        info,bdata=build_tarinfo("./non_words.json",json.dumps(non_words))
        archive.addfile(info, bdata)

        ### data
        tema_list=[]
        pos_list=[]
        desc_list=[]

        # roots
        root_list=[]
        for root in morph_models.Root.objects.filter(language=language):
            R={
                "root": root.root,
                "tema": root.tema_obj.name,
                "description": root.description_obj.name,
                "part_of_speech": root.part_of_speech.name,
            }
            root_list.append(R)
            tema_list.append(root.tema_obj)
            desc_list.append(root.description_obj)
            pos_list.append(root.part_of_speech)
        info,bdata=build_tarinfo("./roots.json",json.dumps(root_list))
        archive.addfile(info, bdata)
        
        # descriptions
        # part of speech
        # temas

        archive.close()
