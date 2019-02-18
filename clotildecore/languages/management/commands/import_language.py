#! /usr/bin/python
# -*- coding: utf-8 -*-

import re,time
import tarfile,json,io
import os,pwd,grp

from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist

from languages import models
from base import models as base_models
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

        pos_dict={}
        desc_dict={}
        tema_dict={}

        # part of speech
        tarinfo=archive.getmember("./part_of_speech.json")
        fd=archive.extractfile(tarinfo)
        data=json.loads(fd.read().decode())
        for name in data:
            pos,created=morph_models.PartOfSpeech.objects.get_or_create(name=name,
                                                                        defaults=data[name])
            pos_dict[name]=pos

        # descriptions
        tarinfo=archive.getmember("./descriptions.json")
        fd=archive.extractfile(tarinfo)
        data=json.loads(fd.read().decode())
        for name in data:
            desc,created=base_models.Description.objects.get_or_create(name=name)
            desc_dict[name]=desc
            for k in data[name]:
                attr,created=base_models.Attribute.objects.get_or_create(name=k)
                val,created=base_models.Value.objects.get_or_create(string=data[name][k])
                entry,created=base_models.Entry.objects.get_or_create(attribute=attr,value=val)
                desc.entries.add(entry)

        # temas
        tarinfo=archive.getmember("./temas.json")
        fd=archive.extractfile(tarinfo)
        data=json.loads(fd.read().decode())
        for name in data:
            tema,created=morph_models.Tema.objects.get_or_create(name=name)
            tema_dict[name]=tema
            for k in data[name]:
                attr,created=morph_models.TemaArgument.objects.get_or_create(name=k)
                val,created=morph_models.TemaValue.objects.get_or_create(name=data[name][k])
                entry,created=morph_models.TemaEntry.objects.get_or_create(argument=attr,value=val,tema=tema)


        # roots
        tarinfo=archive.getmember("./roots.json")
        fd=archive.extractfile(tarinfo)
        data=json.loads(fd.read().decode())
        for root in data:
            tema=tema_dict[root["tema"]]
            pos=pos_dict[root["part_of_speech"]]
            desc=desc_dict[root["description"]]
            val=root["root"]
            obj,created=morph_models.Root.objects.get_or_create(root=val,part_of_speech=pos,
                                                                tema_obj=tema,description_obj=desc,
                                                                language=language)

        # derivations
        # paradigmas
        # fusions

        archive.close()
