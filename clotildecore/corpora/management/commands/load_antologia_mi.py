#! /usr/bin/python
# -*- coding: utf-8 -*-

import re,time

from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist
from corpora.models import Corpus,WDConcorso,WDForum,WDAuthor,WDText
from languages.models import Language

RE_TESTO_CONC=re.compile('(\[?MIB? *[0-9Q]+\])[ -]*(.*)',re.IGNORECASE)
RE_TESTO_RIV=re.compile('(\[RIV\]) *(.*)',re.IGNORECASE)
FID_RACCONTI='27'
FID_MIB='74'
FID_ANTOLOGIA='81'

ANT_CORPUS_ID=1

class Testo(object):
    def __init__(self,testi_dir,autore,aid,forum,tid,titolo,turl,tstamp):
        self.testi_dir=testi_dir
        self.autore=autore
        self.aid=aid
        self.tid=tid
        self.titolo=titolo
        self.revisione=False
        if RE_TESTO_CONC.match(titolo):
            t=RE_TESTO_CONC.findall(titolo)
            self.concorso=t[0][0].replace('[','').replace(']','').replace(' ','').upper()
            self.titolo=t[0][1]
        elif RE_TESTO_RIV.match(titolo):
            self.revisione=True
            t=RE_TESTO_RIV.findall(titolo)
            self.titolo=t[0][1]
            self.concorso="ANT"
        else:
            self.titolo=titolo
            self.concorso="ANT"
        if self.titolo[-1]==".": self.titolo=self.titolo[:-1]
        if self.titolo[-22:]==" - versione definitiva":
            self.titolo=self.titolo[:-22]
        self.titolo=self.titolo.replace('&#33;','!')
        self.titolo=self.titolo.replace('&#39;',"'")
        self.titolo=self.titolo.strip()
        self.turl=turl
        self.tstamp=tstamp
        self.forum=forum
        self.text=""

    def __unicode__(self): 
        if self.revisione: 
            rev="R"
        else:
            rev=" "
        return "%5s %4s %-19.19s %s %s" % (self.tid,self.concorso,self.forum,rev,self.titolo)

    def load(self):
        fd=open(self.testi_dir+"/"+self.tid+".txt","r")
        self.text=fd.read()
        self.text=unicode(self.text,'utf-8')
        fd.close()

class DBForum(object):
    def __init__(self,title):
        self.title=title
        if self.title=="Antologia MI":
            self.wd_id=FID_ANTOLOGIA
        elif self.title=="Racconti":
            self.wd_id=FID_RACCONTI
        else:
            self.wd_id=FID_MIB
        self.wd_id=int(self.wd_id)

    def __unicode__(self):
        return(unicode(self.wd_id)+" - "+self.title)

    def get_db_object(self):
        try:
            c=WDForum.objects.get(wd_id=self.wd_id)
        except ObjectDoesNotExist, e:
            c=WDForum.objects.create(wd_id=self.wd_id,title=self.title)
        return(c)

class DBConcorso(object):
    def __init__(self,tag):
        self.tag=tag
        if self.tag=="ANT":
            self.title="Antologia MI"
        elif self.tag[0:3]=="MIB":
            if self.tag[3:]=="Q":
                self.title="Mezzogiorno d'Inchiostro Birthday (quarti di finale)"
            else:
                self.title="Mezzogiorno d'Inchiostro Birthday (tema %s)" % self.tag[3:]
        else:
            self.title="Mezzogiorno d'Inchiostro %s" % self.tag[2:]

    def __unicode__(self):
        return(self.tag+" - "+self.title)

    def get_db_object(self):
        try:
            c=WDConcorso.objects.get(tag=self.tag)
        except ObjectDoesNotExist, e:
            c=WDConcorso.objects.create(tag=self.tag,title=self.title)
        return(c)

class DBAuthor(object):
    def __init__(self,name,aid):
        self.name=name
        self.wd_id=int(aid)

    def __unicode__(self):
        return(unicode(self.wd_id)+" - "+self.name)

    def get_db_object(self):
        try:
            c=WDAuthor.objects.get(wd_id=self.wd_id)
        except ObjectDoesNotExist, e:
            c=WDAuthor.objects.create(wd_id=self.wd_id,name=self.name)
        return(c)

class DBTesto(object):
    def __init__(self,corpus,testo,autori,concorsi,forum):
        self.corpus = corpus

        self.author = autori[int(testo.aid)]
        self.concorso = concorsi[testo.concorso]
        self.forum = forum[testo.forum]

        self.title = testo.titolo
        self.pub_date = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(int(testo.tstamp)))
        self.wd_id = int(testo.tid)
        testo.load()
        self.text=testo.text

    def get_db_object(self):
        try:
            c=WDText.objects.get(wd_id=self.wd_id)
        except ObjectDoesNotExist, e:
            c=WDText.objects.create(wd_id=self.wd_id,corpus=self.corpus,
                                    author=self.author,concorso=self.concorso,
                                    forum=self.forum,title=self.title,
                                    pub_date=self.pub_date,text=self.text)
        return(c)
        

class Command(BaseCommand):
    args = '<directory>'
    help = 'Load Antologia MI texts'

    def handle(self, *args, **options):
        base_dir=args[0]
        elenco=base_dir+"/elenco.txt"
        testi_dir=base_dir+"/ripuliti"
        testi=[]

        fd=open(elenco,"r")
        for l in fd.readlines():
            l=unicode(l,'utf-8')
            l=l.strip()
            if not l: continue
            l=l.replace(':http://www.writersdream.org/forum/topic/',':')
            l=l.replace('/','')
            (begin,end,aid,tid,aname,titolo,forum,turl,tstamp)=l.split(':')
            t=Testo(testi_dir,aname,aid,forum,tid,titolo,turl,tstamp)
            testi.append(t)
        fd.close()

        #for t in testi:
        #    print unicode(t)

        concorsi=map(DBConcorso,list(set(map(lambda x: x.concorso,testi))))
        db_concorsi={}
        for c in concorsi:
            print "concorso",unicode(c)
            db_c=c.get_db_object()
            db_concorsi[c.tag]=db_c

        forum=map(DBForum,list(set(map(lambda x: x.forum,testi))))
        db_forum={}
        for f in forum:
            print "forum",unicode(f)
            db_f=f.get_db_object()
            db_forum[f.title]=db_f
        print

        autori=map(lambda (a,b): DBAuthor(a,b),
                   list(set(map(lambda x: (x.autore,x.aid),testi))))
        db_autori={}
        for a in autori:
            print "autori",unicode(a)
            db_a=a.get_db_object()
            db_autori[a.wd_id]=db_a

        desc = "Corpus dei racconti selezionati per l'Antologia MI di Wirter's Dream"
        lang = Language.objects.get(name="italiano")
        corpus,created=Corpus.objects.get_or_create(name="Antologia MI",
                                                    defaults={'description':desc,
                                                              'language': lang})

        for t in testi:
            d_t=DBTesto(corpus,t,db_autori,db_concorsi,db_forum)
            db_t=d_t.get_db_object()
                