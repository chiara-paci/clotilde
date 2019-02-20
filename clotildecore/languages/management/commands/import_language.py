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
            w,created=models.NonWord.objects.get_or_create(language=language,word=non_words[k],
                                                           defaults={"name": k})
            w.name=k
            w.save()

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
            ok=[]
            desc_dict[name]=desc
            for k in data[name]:
                attr,created=base_models.Attribute.objects.get_or_create(name=k)
                val,created=base_models.Value.objects.get_or_create(string=data[name][k])
                entry,created=base_models.Entry.objects.get_or_create(attribute=attr,value=val)
                ok.append(entry.pk)
                desc.entries.add(entry)
            desc.entries.remove(*desc.entries.exclude(pk__in=ok))

        # temas
        tarinfo=archive.getmember("./temas.json")
        fd=archive.extractfile(tarinfo)
        data=json.loads(fd.read().decode())
        for name in data:
            tema,created=morph_models.Tema.objects.get_or_create(name=name)
            tema_dict[name]=tema
            ok=[]
            for k in data[name]:
                attr,created=morph_models.TemaArgument.objects.get_or_create(name=k)
                val,created=morph_models.TemaValue.objects.get_or_create(name=data[name][k])
                entry,created=morph_models.TemaEntry.objects.get_or_create(argument=attr,value=val,tema=tema)
                ok.append(entry.pk)
            morph_models.TemaEntry.objects.filter(tema=tema).exclude(pk__in=ok).delete()

        # roots
        tarinfo=archive.getmember("./roots.json")
        fd=archive.extractfile(tarinfo)
        data=json.loads(fd.read().decode())
        root_ok=[]
        for root in data:
            tema=tema_dict[root["tema"]]
            pos=pos_dict[root["part_of_speech"]]
            desc=desc_dict[root["description"]]
            val=root["root"]
            obj,created=morph_models.Root.objects.get_or_create(root=val,part_of_speech=pos,
                                                                tema_obj=tema,description_obj=desc,
                                                                language=language)
            root_ok.append(obj.pk)

        # paradigmas
        par_dict={}
        par_ok=[]
        for tarinfo in archive.getmembers():
            if not tarinfo.name.startswith('./paradigmas/'): continue
            fd=archive.extractfile(tarinfo)
            data=json.loads(fd.read().decode())
            pos=pos_dict[data["part_of_speech"]]
            par,created=morph_models.Paradigma.objects.get_or_create(name=data["name"],
                                                                     defaults={"language":language,
                                                                               "part_of_speech":pos})
            par_ok.append(par.pk)
            par_dict[data["name"]]=par
            ok=[]
            for infl in data["inflections"]:
                desc=desc_dict[infl["description"]]
                regsub,created=morph_models.RegexpReplacement.objects.get_or_create(pattern=infl["regsub"][0],
                                                                                    replacement=infl["regsub"][1])
                obj,created=morph_models.Inflection.objects.get_or_create(regsub=regsub,description_obj=desc)
                obj.dict_entry=infl["dict_entry"]
                obj.save()
                par.inflections.add(obj)
                ok.append(obj.pk)
            par.inflections.remove(*par.inflections.exclude(pk__in=ok))

        # derivations
        tarinfo=archive.getmember("./derivations.json")
        fd=archive.extractfile(tarinfo)
        data=json.loads(fd.read().decode())
        der_ok=[]
        for name in data:
            regsub,created=morph_models.RegexpReplacement.objects.get_or_create(pattern=data[name]["regsub"][0],
                                                                                replacement=data[name]["regsub"][1])
            tema=tema_dict[data[name]["tema"]]
            desc=desc_dict[data[name]["description"]]
            r_desc=desc_dict[data[name]["root_description"]]
            r_pos=pos_dict[data[name]["root_part_of_speech"]]
            par=par_dict[data[name]["paradigma"]]
            der,created=morph_models.Derivation.objects.get_or_create(name=name,language=language,
                                                                      defaults={
                                                                          "regsub": regsub,
                                                                          "tema_obj": tema,
                                                                          "description_obj": desc,
                                                                          "root_description_obj": r_desc,
                                                                          "root_part_of_speech": r_pos,
                                                                          "paradigma": par,
                                                                      })
            der.regsub=regsub
            der.tema_obj=tema
            der.description_obj=desc
            der.root_description_obj=r_desc
            der.root_part_of_speech_obj=r_pos
            der.paradigma=par
            der.save()
            der_ok.append(der.pk)
            
        # fusions

        tarinfo=archive.getmember("./fusions.json")
        fd=archive.extractfile(tarinfo)
        data=json.loads(fd.read().decode())
        fusion_ok=[]
        for name in data:
            fusion,created=morph_models.Fusion.objects.get_or_create(name=name,language=language)
            fusion_ok.append(fusion.pk)
            n=0
            ok=[]
            for rule in data[name]:
                regsub,created=morph_models.RegexpReplacement.objects.get_or_create(pattern=rule["regsub"][0],
                                                                                    replacement=rule["regsub"][1])

                tema=tema_dict[rule["tema"]]
                desc=desc_dict[rule["description"]]
                pos=pos_dict[rule["part_of_speech"]]
                
                frule,created=morph_models.FusionRule.objects.get_or_create(name=rule["name"],
                                                                            defaults={
                                                                                "tema_obj": tema,
                                                                                "part_of_speech": pos,
                                                                                "description_obj": desc,
                                                                                "regsub": regsub
                                                                            })
                frule.tema_obj=tema
                frule.part_of_speech=pos
                frule.description_obj=desc
                frule.regsub=regsub
                frule.save()
                rel,created=morph_models.FusionRuleRelation.objects.get_or_create(fusion_rule=frule,
                                                                                  fusion=fusion,order=n)
                n+=1
                ok.append(rel.pk)

            morph_models.FusionRuleRelation.objects.filter(fusion=fusion).exclude(pk__in=ok).delete()


        morph_models.Fusion.objects.filter(language=language).exclude(pk__in=fusion_ok).delete()
        morph_models.Root.objects.filter(language=language).exclude(pk__in=root_ok).delete()
        morph_models.Derivation.objects.filter(language=language).exclude(pk__in=der_ok).delete()
        morph_models.Paradigma.objects.filter(language=language).exclude(pk__in=par_ok).delete()

        archive.close()
