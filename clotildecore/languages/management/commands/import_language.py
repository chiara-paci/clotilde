#! /usr/bin/python
# -*- coding: utf-8 -*-

import re,time
import tarfile,json,io
import os,pwd,grp

from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist

from languages import models
from base import models as base_models

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
    help = 'Import language from file <fname.lar>'

    def add_arguments(self, parser):
        parser.add_argument(
            'fname',
            help='filename',
        )

    def handle(self, *args, **options):
        fname = options["fname"]

        archive=tarfile.open(name=fname, mode='r:bz2')

        ## language
        m_index=archive.getmember("./index.json")
        fd=archive.extractfile(m_index)
        index=json.loads(fd.read().decode())

        alphabetic_order=base_models.AlphabeticOrder.objects.de_serialize(index["alphabetic_order"])
        case_set=base_models.CaseSet.objects.de_serialize(index["case_set"])
        trexp_set=base_models.TokenRegexpSet.objects.de_serialize(index["token_regexp_set"])
        period=base_models.TokenRegexp.objects.get(name=index["period_sep"])

        language,created=models.Language.objects.get_or_create(name=index["name"],
                                                               token_regexp_set = trexp_set,
                                                               case_set = case_set,
                                                               alphabetic_order = alphabetic_order,
                                                               defaults={
                                                                   "period_sep": period,
                                                               })
        
        ## non-words
        m_non_words=archive.getmember("./non_words.json")
        fd=archive.extractfile(m_non_words)
        non_words=json.loads(fd.read().decode())
        for k in non_words:
            models.NonWord.objects.get_or_create(language=language,word=non_words[k],
                                                 defaults={"name": k})

        archive.close()
