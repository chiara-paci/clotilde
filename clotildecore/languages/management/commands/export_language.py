#! /usr/bin/python
# -*- coding: utf-8 -*-

import re,time
import tarfile,json,io
import os,pwd,grp

from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist

from languages import models
from morphology import models as morph_models
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
            root_list.append(root.serialize())
            tema_list.append(root.tema_obj.pk)
            # desc_list.append(root.description_obj.pk)
            pos_list.append(root.part_of_speech.pk)
        info,bdata=build_tarinfo("./roots.json",json.dumps(root_list))
        archive.addfile(info, bdata)

        # derivations
        der_list=[]
        for der in morph_models.Derivation.objects.filter(language=language):
            der_list.append(der.serialize())
            # tema_list.append(der.tema_obj.pk)
            desc_list.append(der.description_obj.pk)
            # desc_list.append(der.root_description_obj.pk)
            pos_list.append(der.root_part_of_speech.pk)
        info,bdata=build_tarinfo("./derivations.json",json.dumps(dict(der_list)))
        archive.addfile(info, bdata)

        # paradigmas
        par_list=[]
        for par in morph_models.Paradigma.objects.filter(language=language):
            infl_list=list(par.inflections.all())
            desc_list+=[ infl.description_obj.pk for infl in infl_list ]
            infl_list=[ infl.serialize() for infl in infl_list ]
            pos_list.append(par.part_of_speech.pk)
            par_obj={
                "name": par.name,
                "part_of_speech": par.part_of_speech.name,
                "inflections": infl_list
            } 

            info,bdata=build_tarinfo("./paradigmas/%s.json" % functions.slugify(par.name),json.dumps(par_obj))
            archive.addfile(info, bdata)

        # fusion
        fusion_list=[]
        for fusion in morph_models.Fusion.objects.filter(language=language):
            rule_list=[ rel.fusion_rule for rel in fusion.fusionrulerelation_set.all() ]
            for rule in rule_list:
                desc_list.append(rule.description_obj.pk)
                tema_list.append(rule.tema_obj.pk)
                pos_list.append(rule.part_of_speech.pk)
            fusion_list.append( ( fusion.name, [rule.serialize() for rule in rule_list] ) )
        info,bdata=build_tarinfo("./fusions.json",json.dumps(dict(fusion_list)))
        archive.addfile(info, bdata)
        
        # descriptions
        # part of speech
        # temas
        desc_list=list(set(desc_list))
        tema_list=list(set(tema_list))
        pos_list=list(set(pos_list))

        tema_list=dict([ d.serialize() for d in morph_models.Tema.objects.filter(pk__in=tema_list)])
        pos_list =dict([ d.serialize() for d in morph_models.PartOfSpeech.objects.filter(pk__in=pos_list)])

        desc_qset=base_models.Description.objects.filter(pk__in=desc_list)
        desc_list=dict([ d.serialize() for d in desc_qset])

        entry_list=desc_qset.values("entries")

        desc_values={
            "attributes": [ attr.serialize() for attr in base_models.Attribute.objects.filter(entry__in=entry_list).distinct() ],
            "values":     [ val.serialize()  for val  in base_models.Value.objects.filter(entry__in=entry_list).distinct() ],
        }

        info,bdata=build_tarinfo("./description_values.json",json.dumps(desc_values))
        archive.addfile(info, bdata)

        info,bdata=build_tarinfo("./descriptions.json",json.dumps(desc_list))
        archive.addfile(info, bdata)

        info,bdata=build_tarinfo("./temas.json",json.dumps(tema_list))
        archive.addfile(info, bdata)

        info,bdata=build_tarinfo("./part_of_speech.json",json.dumps(pos_list))
        archive.addfile(info, bdata)

        archive.close()
