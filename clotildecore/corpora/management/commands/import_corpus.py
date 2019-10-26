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
    help = 'Import corpus from file <fname.car>'

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

        language=lang_models.Language.objects.get(name=index["language"])

        corpus,created=models.Corpus.objects.update_or_create(name=index["name"],language=language,
                                                              defaults={"description": index["description"]})
        text_ok=[]
        for tdata in index["texts"]:
            author,created=models.Author.objects.get_or_create(name=tdata["author"])
            m_txt=archive.getmember("./%s" % tdata["file_name"])
            fd=archive.extractfile(m_txt)
            txt=fd.read().decode()
            if ( ("label" in tdata) and (tdata["label"]!="") ):
                label=tdata["label"]
            else:
                label=tdata["file_name"].replace(".txt","")
            
            text,created=models.Text.objects.update_or_create(corpus=corpus,
                                                              author=author,
                                                              label=label,
                                                              defaults={
                                                                  title=tdata["title"],
                                                                  "text": txt
                                                              })
            text_ok.append(text.pk)
            m_ok=[]
            for k,val in tdata["metadata"]:
                arg,created=models.MetaDataArgument.objects.get_or_create(name=k)
                entry,created=models.MetaDataEntry.objects.update_or_create(text=text,argument=arg,
                                                                            defaults={"value":val})
                m_ok.append(entry.pk)
            models.MetaDataEntry.objects.filter(text=text).exclude(pk__in=m_ok).delete()

        models.Text.objects.filter(corpus=corpus).exclude(pk__in=text_ok).delete()

        archive.close()
