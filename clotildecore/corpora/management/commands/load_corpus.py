#! /usr/bin/python
# -*- coding: utf-8 -*-

import tarfile
import json

from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist

from corpora import models
from base import models as base_models

# fcar must be a bz2 compressed tar, containing a file index.json:
# {
#    "name": "Novelle di Verga",
#    "language": "italiano",
#    "description": "Tutte le novelle di Verga, preso da LiberLiber"
# }
# and one json file for each text:
# {
#    "title": "Novella 1",
#    "author": "Giovanni Verga",
#    "text": "Testo del racconto..."
# }

class Command(BaseCommand):
    requires_migrations_checks = True
    help = 'Import corpus from file <fcar>'

    def add_arguments(self, parser):
        parser.add_argument(
            'fcar',
            help='file car (Corpus ARchive)',
        )

    def handle(self, *args, **options):
        fcar = options["fcar"]

        archive=tarfile.open(name=fcar, mode='r:bz2')
        m_index=archive.getmember("./index.json")

        fd=archive.extractfile(m_index)
        index=json.loads(fd.read().decode())

        language=base_models.Language.objects.get(name=index["language"])

        corpus,created=models.Corpus.objects.get_or_create(name=index["name"],
                                                           defaults={
                                                               "language": language,
                                                               "description": index["description"]
                                                           })

        for m in archive.getmembers():
            if m==m_index: continue
            if not m.isfile(): continue
            fd=archive.extractfile(m)
            print(m)
            obj=json.loads(fd.read().decode())
            author,created=models.Author.objects.get_or_create(name=obj["author"])
            models.Text.objects.get_or_create(corpus=corpus,title=obj["title"],author=author,
                                              defaults={"text": obj["text"]})
            
            #print(m)

        archive.close()

        # case_set,created=models.CaseSet.objects.get_or_create(name=name)

        # #fname=args[0]
        # with open(fname,'r') as fd:
        #     for r in fd.readlines():
        #         r=r.strip()
        #         if not r: continue
        #         if r.startswith('#'): continue
        #         t=r.split(":")
        #         if len(t)<2: continue
        #         case_pair,created=models.CasePair.objects.get_or_create(lower=t[0],upper=t[1])
        #         case_set.pairs.add(case_pair)
