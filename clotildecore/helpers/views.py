from django.shortcuts import render
from django.utils.translation import ugettext as _
from django.db.models import Count

from django.views.generic import TemplateView,DetailView,View
from django.views.generic.detail import SingleObjectMixin
from django import forms
from django.shortcuts import render,redirect
from django.urls import reverse
from django.forms.formsets import  ORDERING_FIELD_NAME,DELETION_FIELD_NAME

import collections,re

from morphology  import models as morph_models
from languages  import models as lang_models
from base  import models as base_models

from corpora  import models as corp_models
from corpora  import views as corp_views

# Create your views here.

class ItalianoView(TemplateView):
    template_name="helpers/italiano/index.html"
 
    def get_context_data(self,**kwargs):
        context=TemplateView.get_context_data(self,**kwargs)
        language=lang_models.Language.objects.get(name="italiano")
        context["language"]=language
        return context

class ItalianoTextCollectorView(View,SingleObjectMixin):
    model=corp_models.Text

    class InnerViewMixin(object):
        class BaseForm(forms.Form):
            root = forms.CharField(widget=forms.TextInput(attrs={'class':'field_root'}))

            def as_table(self):
                "Return this form rendered as HTML <tr>s -- excluding the <table></table>."
                ret=self._html_output(
                    normal_row='<td>%(errors)s%(field)s%(help_text)s</td>',
                    error_row='<td colspan="2">%s</td>',
                    row_ender='</td>',
                    help_text_html='<br><span class="helptext">%s</span>',
                    errors_on_separate_row=False,
                )
                return ret.replace("\n","")

        class BaseFormSet(forms.BaseFormSet):

            def add_fields(self, form, index):
                """A hook for adding extra fields on to each form instance."""
                w_delete=forms.CheckboxInput(attrs={"class":"field_delete"})
                w_order=forms.NumberInput(attrs={"class":"field_order"})
                if self.can_order:
                    # Only pre-fill the ordering field for initial forms.
                    if index is not None and index < self.initial_form_count():
                        form.fields[ORDERING_FIELD_NAME] = forms.IntegerField(label=_(u'Order'),
                                                                              initial=index+1,
                                                                              required=False,
                                                                              widget=w_order)
                    else:
                        form.fields[ORDERING_FIELD_NAME] = forms.IntegerField(label=_(u'Order'),
                                                                              required=False,
                                                                              widget=w_order)


                if self.can_delete:
                    form.fields[DELETION_FIELD_NAME] = forms.BooleanField(label=_(u'Delete'), required=False,
                                                                          widget=w_delete)

        def _form_pos_decorator(self,C,part_of_speech):
            #part_of_speech=morph_models.PartOfSpeech.objects.get(name=part_of_speech)
            qset=morph_models.Tema.objects.by_part_of_speech(part_of_speech)
            class DecoratedForm(C):
                tema = forms.ModelChoiceField(queryset=qset,empty_label=None)
            return DecoratedForm

        def _formset_factory(self,part_of_speech):
            return forms.formset_factory(self._form_pos_decorator(self.BaseForm,part_of_speech),
                                         formset=self.BaseFormSet,
                                         extra=0,can_delete=True,can_order=False,
                                         max_num=1, min_num=1)
    
    class InnerGetView(corp_views.TextMorphologicalParserView,InnerViewMixin):
        template_name="helpers/italiano/text_collector.html"

        def get_context_data(self,**kwargs):
            context=corp_views.TextMorphologicalParserView.get_context_data(self,**kwargs)
            VerboBaseFormset     = self._formset_factory("verbo")
            NomeBaseFormset      = self._formset_factory("nome")
            AggettivoBaseFormset = self._formset_factory("aggettivo")
            context["formsets"]={
                "nome":      NomeBaseFormset(prefix="nome"),
                "verbo":     VerboBaseFormset(prefix="verbo"),
                "aggettivo": AggettivoBaseFormset(prefix="aggettivo")
            }
            return context

    class InnerPostView(corp_views.TextMorphologicalParserView,InnerViewMixin):
        template_name="helpers/italiano/text_collector.html"
        success_url = None

        class Creator(object):
            description="vuota"
            
            def __init__(self,part_of_speech):
                self._part_of_speech=morph_models.PartOfSpeech.objects.get(name=part_of_speech)
                self._language=lang_models.Language.objects.get(name="italiano")
                self._description=base_models.Description.objects.get(name=self.description)

            def __call__(self,cleaned_data):
                root=cleaned_data["root"]
                tema=cleaned_data["tema"]
                obj,created=morph_models.Root.objects.get_or_create(root=root,tema_obj=tema,
                                                                    language=self._language,
                                                                    part_of_speech=self._part_of_speech,
                                                                    description_obj=self._description)
                if not created: return obj
                obj.update_derived()
                return obj

        creators={
            "nome": Creator("nome"),
            "verbo": Creator("verbo"),
            "aggettivo": Creator("aggettivo"),
        }
            
        def post(self,request,*args,**kwargs):
            self.object=self.get_object()
            VerboBaseFormset     = self._formset_factory("verbo")
            NomeBaseFormset      = self._formset_factory("nome")
            AggettivoBaseFormset = self._formset_factory("aggettivo")

            formsets = {
                "nome":      NomeBaseFormset(request.POST, request.FILES,prefix="nome"),
                "verbo":     VerboBaseFormset(request.POST, request.FILES,prefix="verbo"),
                "aggettivo": AggettivoBaseFormset(request.POST, request.FILES,prefix="aggettivo"),
            }

            for k in [ "nome","verbo","aggettivo" ]:
                if not formsets[k].is_valid():
                    context=self.get_context_data()
                    context["formsets"]=formsets
                    print("formset",k,request.POST)
                    return render(request,self.template_name,context)
                for form in formsets[k]:
                    if not form.is_valid():
                        context=self.get_context_data()
                        context["formsets"]=formsets
                        print("formset",k,"form",form)
                        return render(request,self.template_name,context)

            for k in [ "nome","verbo","aggettivo" ]:
                for form in formsets[k]:
                    if form.cleaned_data[DELETION_FIELD_NAME]: continue
                    self.creators[k]( form.cleaned_data )
            return redirect(self.success_url)

    def get(self,request, *args, **kwargs):
        view=self.InnerGetView.as_view()
        response=view(request,*args,**kwargs)
        return response

    def post(self,request, *args, **kwargs):
        obj=self.get_object()
        success_url=reverse("helpers:italiano_textcollector", kwargs={'pk': obj.pk})
        view=self.InnerPostView.as_view(success_url=success_url)
        response=view(request,*args,**kwargs)
        return response

    



    
        

class ItalianoVerbiView(TemplateView):
    template_name="helpers/italiano/verbi.html"

    class FiniteForm(forms.Form):
        pattern = forms.CharField(initial="(.+)",widget=forms.TextInput(attrs={'size':10}))
        replacement = forms.CharField(initial=r"\1",widget=forms.TextInput(attrs={'size':10}))
        person = forms.ChoiceField( choices=[( "prima singolare", "prima singolare" ),
                                             ( "seconda singolare", "seconda singolare" ),
                                             ( "terza singolare", "terza singolare" ),
                                             ( "prima plurale", "prima plurale" ),
                                             ( "seconda plurale", "seconda plurale" ),
                                             ( "terza plurale", "terza plurale" )] )

    class InfiniteForm(forms.Form):
        pattern = forms.CharField(initial="(.+)",widget=forms.TextInput(attrs={'size':10}))
        replacement = forms.CharField(initial=r"\1",widget=forms.TextInput(attrs={'size':10}))

    class ParticipeForm(forms.Form):
        pattern = forms.CharField(initial="(.+)",widget=forms.TextInput(attrs={'size':10}))
        replacement = forms.CharField(initial=r"\1",widget=forms.TextInput(attrs={'size':10}))
        gennum = forms.ChoiceField( choices=[( "maschile singolare", "maschile singolare" ),
                                             ( "femminile singolare", "femminile singolare" ),
                                             ( "maschile plurale", "maschile plurale" ),
                                             ( "femminile plurale", "femminile plurale" )] )

    
    class BaseForm(forms.Form):
        remove = forms.BooleanField(required=False)

    class ParadigmaForm(forms.Form):
        name = forms.CharField()
        template = forms.ModelChoiceField(queryset=morph_models.Paradigma.objects.filter(language__name="italiano",
                                                                                         part_of_speech__name="verbo"),required=False)

    combination=[
        ("indicativo","presente","finite"),
        ("indicativo","imperfetto","finite"),
        ("indicativo","passato remoto","finite"),
        ("indicativo","futuro","finite"),
        ("congiuntivo","presente","finite"),
        ("congiuntivo","imperfetto","finite"),
        ("condizionale","presente","finite"),
        ("imperativo","presente","finite"),
        ("infinito","presente","infinite"),
        ("gerundio","presente","infinite"),
        ("participio","presente","participe"),
        ("participio","passato","participe"),
    ]

    finite_initial=[
        {"person": "prima singolare"},
        {"person": "seconda singolare"},
        {"person": "terza singolare"},
        {"person": "prima plurale"},
        {"person": "seconda plurale"},
        {"person": "terza plurale"},
    ]

    participe_initial=[
        {"gennum": "maschile singolare"},
        {"gennum": "femminile singolare"},
        {"gennum": "maschile plurale"},
        {"gennum": "femminile plurale"},
    ]

    FiniteFormset=forms.formset_factory(FiniteForm,extra=0,can_delete=False,can_order=False,
                                        max_num=len(finite_initial), min_num=len(finite_initial))

    ParticipeFormset=forms.formset_factory(ParticipeForm,extra=0,can_delete=False,can_order=False,
                                           max_num=len(participe_initial), min_num=len(participe_initial))


    def get_context_data(self,**kwargs):
        context=TemplateView.get_context_data(self,**kwargs)

        sections=collections.OrderedDict()
        for modo,tempo,is_finite in self.combination:
            prefix="%s_%s" % (modo,tempo.replace(" ","_"))
            obj={
                "form": self.BaseForm(prefix=prefix), #,initial={"tempo": tempo,"modo": modo}),
                "is_finite": is_finite
            }
            if is_finite=="finite":
                obj["formset_re"]=self.FiniteFormset(prefix=prefix+"_re",initial=self.finite_initial)
            elif is_finite=="participe":
                obj["formset_re"]=self.ParticipeFormset(prefix=prefix+"_re",initial=self.participe_initial)
            else:
                obj["form_re"]=self.InfiniteForm(prefix=prefix+"_re")

            if modo not in sections: sections[modo]=collections.OrderedDict()
            sections[modo][tempo]=obj

        context["sections"]=sections
        context["paradigma_form"]=self.ParadigmaForm(prefix="paradigma")
        return context

    def post(self,request,*args,**kwargs):
        paradigma_form=self.ParadigmaForm(prefix="paradigma",data=request.POST)
        sections=collections.OrderedDict()
        for modo,tempo,is_finite in self.combination:
            prefix="%s_%s" % (modo,tempo.replace(" ","_"))
            obj={
                "form": self.BaseForm(prefix=prefix,data=request.POST), #,initial={"tempo": tempo,"modo": modo}),
                "is_finite": is_finite
            }
            if is_finite=="finite":
                obj["formset_re"]=self.FiniteFormset(prefix=prefix+"_re",data=request.POST)
            elif is_finite=="participe":
                obj["formset_re"]=self.ParticipeFormset(prefix=prefix+"_re",data=request.POST)
            else:
                obj["form_re"]=self.InfiniteForm(prefix=prefix+"_re",data=request.POST)

            if modo not in sections: sections[modo]=collections.OrderedDict()
            sections[modo][tempo]=obj

        if not paradigma_form.is_valid():
            context=self.get_context_data()
            context["sections"]=sections
            context["paradigma_form"]=paradigma_form
            print(paradigma_form.errors)
            return render(request,self.template_name,context)

        for modo,tempo,is_finite in self.combination:
            if not sections[modo][tempo]["form"].is_valid():
                context=self.get_context_data()
                context["sections"]=sections
                context["paradigma_form"]=paradigma_form
                print(sections[modo][tempo]["form"].errors)
                return render(request,self.template_name,context)
            if is_finite!="infinite":
                if not sections[modo][tempo]["formset_re"].is_valid():
                    context=self.get_context_data()
                    context["sections"]=sections
                    context["paradigma_form"]=paradigma_form
                    print(sections[modo][tempo]["formset_re"].errors)
                    return render(request,self.template_name,context)
            else:
                if not sections[modo][tempo]["form_re"].is_valid():
                    context=self.get_context_data()
                    context["sections"]=sections
                    context["paradigma_form"]=paradigma_form
                    print(sections[modo][tempo]["form_re"].errors)
                    return render(request,self.template_name,context)

        language,created=lang_models.Language.objects.get_or_create(name="italiano")
        pos,created=morph_models.PartOfSpeech.objects.get_or_create(name="verbo")

        name=paradigma_form.cleaned_data["name"]
        paradigma,created=morph_models.Paradigma.objects.get_or_create(name=name,
                                                                       language=language,
                                                                       part_of_speech=pos)

        print("create %s",paradigma)

        for modo,tempo,is_finite in self.combination:
            base=sections[modo][tempo]["form"].cleaned_data
            if base["remove"]: continue
            if is_finite=="infinite":
                data=sections[modo][tempo]["form_re"].cleaned_data
                pattern=data["pattern"]
                replacement=data["replacement"]
                regsub,created=morph_models.RegexpReplacement.objects.get_or_create(pattern=pattern,replacement=replacement)
                desc,created=base_models.Description.objects.get_or_create_by_dict("%s %s" % (modo,tempo), {"modo": modo, "tempo": tempo})
                dict_entry=( modo=="infinito" and tempo=="presente" )
                infl,created=morph_models.Inflection.objects.get_or_create(dict_entry=dict_entry,regsub=regsub,description_obj=desc)
                paradigma.inflections.add(infl)
                continue
            if is_finite=="finite":
                for form in sections[modo][tempo]["formset_re"]:
                    data=form.cleaned_data
                    person=data["person"]
                    if modo=="imperativo" and person=="prima singolare": continue
                    pattern=data["pattern"]
                    replacement=data["replacement"]
                    regsub,created=morph_models.RegexpReplacement.objects.get_or_create(pattern=pattern,replacement=replacement)
                    t=person.split(" ")
                    desc,created=base_models.Description.objects.get_or_create_by_dict("%s %s %s" % (modo,tempo,person), 
                                                                                       {"modo": modo, "tempo": tempo,"persona": t[0],"numero": t[1]})
                    infl,created=morph_models.Inflection.objects.get_or_create(dict_entry=False,regsub=regsub,description_obj=desc)
                    paradigma.inflections.add(infl)
                continue
            for form in sections[modo][tempo]["formset_re"]:
                data=form.cleaned_data
                pattern=data["pattern"]
                replacement=data["replacement"]
                regsub,created=morph_models.RegexpReplacement.objects.get_or_create(pattern=pattern,replacement=replacement)
                gennum=data["gennum"]
                t=gennum.split(" ")
                desc,created=base_models.Description.objects.get_or_create_by_dict("%s %s %s" % (modo,tempo,gennum), 
                                                                                   {"modo": modo, "tempo": tempo,"genere": t[0],"numero": t[1]})
                infl,created=morph_models.Inflection.objects.get_or_create(dict_entry=False,regsub=regsub,description_obj=desc)
                paradigma.inflections.add(infl)
            continue
            


        return redirect("/helpers/italiano/verbi/")


class ItalianoAddRootView(TemplateView):
    template_name="helpers/italiano/add_root.html"

    class RootForm(forms.Form):
        root = forms.CharField()
        part_of_speech = forms.ModelChoiceField(queryset=morph_models.PartOfSpeech.objects.all(),empty_label=None)
        base = forms.ChoiceField(choices=[ (x["value__name"],x["value__name"]) 
                                           for x in morph_models.TemaEntry.objects.filter(argument__name="base").values("value__name").distinct().order_by("value__name") ])

    class DerivatoForm(forms.Form):
        pattern = forms.CharField(initial="(.+)")
        replacement = forms.CharField(initial=r"\\1")

        def as_table(self):
            "Return this form rendered as HTML <tr>s -- excluding the <table></table>."
            ret=self._html_output(
                normal_row='<td>%(errors)s%(field)s%(help_text)s</td>',
                error_row='<td colspan="2">%s</td>',
                row_ender='</td>',
                help_text_html='<br><span class="helptext">%s</span>',
                errors_on_separate_row=False,
            )
            return ret.replace("\n","")


    def _form_pos_decorator(self,C,part_of_speech):
        qset=morph_models.Paradigma.objects.filter(part_of_speech__name=part_of_speech)
        class DecoratedForm(C):
            paradigma = forms.ModelChoiceField(queryset=qset,empty_label=None)
        return DecoratedForm

    def _formset_factory(self,part_of_speech):
        return forms.formset_factory(self._form_pos_decorator(self.DerivatoForm,part_of_speech),
                                     extra=0,can_delete=True,can_order=False,
                                     max_num=1, min_num=1)

    def get_context_data(self,**kwargs):
        context=TemplateView.get_context_data(self,**kwargs)
        context["form_root"]=self.RootForm(prefix="root")
        context["formsets"]=collections.OrderedDict()
        context["formsets"]["nome"]      = self._formset_factory("nome")(prefix="nome")
        context["formsets"]["verbo"]     = self._formset_factory("verbo")(prefix="verbo")
        context["formsets"]["avverbio"]  = self._formset_factory("avverbio")(prefix="avverbio")
        context["formsets"]["aggettivo"] = self._formset_factory("aggettivo")(prefix="aggettivo")
        return context

    

    class Creator(object):
        description="vuota"

        def __init__(self,part_of_speech):
            self._part_of_speech=part_of_speech
            self._language=lang_models.Language.objects.get(name="italiano")
            self._vuota=base_models.Description.objects.get(name=self.description)

        def _label(self,regsub,paradigma):
            label=re.sub(r'\\[0-9]+','- -',str(regsub.replacement))
            if label.startswith('- -'): label=label[1:]
            if label.endswith('- -'):   label=label[:-1]
            label=label.strip()

            t=[ x.strip() for x in paradigma.name.split("-")]
            if len(t)==1: return label
            
            if len(t)==2:
                suffix=t[1]
            else:
                if t[1]=="c/g":
                    suffix="".join(t[2:])
                else:
                    suffix="".join(t[1:])

            if suffix[0]=="i":
                if label[-1]=="i":
                    return label+suffix[1:]
            return label+suffix

        def _build_derivation(self,root_part_of_speech,regsub,paradigma):
            L=list( morph_models.Derivation.objects.filter(regsub=regsub,
                                                           language=self._language,
                                                           root_description_obj=self._vuota,
                                                           paradigma=paradigma,
                                                           root_part_of_speech=root_part_of_speech) )

            if L: return L[0]
            L=list( morph_models.Derivation.objects.filter(regsub=regsub,
                                                           language=self._language,
                                                           root_description_obj=self._vuota,
                                                           paradigma=paradigma) )
            if L:
                name=L[0].name
                if '(da' in L[0].name:
                    name=re.sub(r'\(da .+?\)','(da %s)' % root_part_of_speech.name,name)
                else:
                    name+=" (da %s)" % root_part_of_speech.name
                derivation=morph_models.Derivation.objects.create(name=name,
                                                                  tema_obj=L[0].tema_obj,
                                                                  regsub=regsub,
                                                                  language=self._language,
                                                                  root_description_obj=self._vuota,
                                                                  description_obj=L[0].description_obj,
                                                                  paradigma=paradigma,
                                                                  root_part_of_speech=root_part_of_speech)
                return derivation
            
            label=self._label(regsub,paradigma)

            name="%s derivato in %s" % (self._part_of_speech,label)

            tema_argument,created=morph_models.TemaArgument.objects.get_or_create(name="%s derivato" % self._part_of_speech)
            tema_value,created=morph_models.TemaValue.objects.get_or_create(name=label)

            L_entry=morph_models.TemaEntry.objects.filter(argument=tema_argument,value=tema_value)

            if L_entry:
                L_tema=morph_models.Tema.objects.filter(pk__in=L_entry.values("tema")).annotate(count=Count("temaentry")).filter(count=1)
                if L_tema:
                    tema_obj=L_tema[0]
                    name+=" (da %s)" % root_part_of_speech.name
                    derivation=morph_models.Derivation.objects.create(name=name,
                                                                      tema_obj=tema_obj,
                                                                      regsub=regsub,
                                                                      language=self._language,
                                                                      root_description_obj=self._vuota,
                                                                      description_obj=self._vuota,
                                                                      paradigma=paradigma,
                                                                      root_part_of_speech=root_part_of_speech)
                    return derivation

            tema_obj=morph_models.Tema.objects.create(name=name)
            t_entry=morph_models.TemaEntry.objects.create(tema=tema_obj,argument=tema_argument,value=tema_value)

            name+=" (da %s)" % root_part_of_speech.name
            derivation=morph_models.Derivation.objects.create(name=name,
                                                              tema_obj=tema_obj,
                                                              regsub=regsub,
                                                              language=self._language,
                                                              root_description_obj=self._vuota,
                                                              description_obj=self._vuota,
                                                              paradigma=paradigma,
                                                              root_part_of_speech=root_part_of_speech)
            return derivation


        def __call__(self,root_part_of_speech,cleaned_data):
            obj=None
            paradigma=cleaned_data["paradigma"]
            replacement=cleaned_data["replacement"]
            pattern=cleaned_data["pattern"]
            regsub,created=morph_models.RegexpReplacement.objects.get_or_create(pattern=pattern,replacement=replacement)
            derivation=self._build_derivation(root_part_of_speech,regsub,paradigma)
            return derivation.tema_obj

    creators={
        "nome": Creator("nome"),
        "verbo": Creator("verbo"),
        "aggettivo": Creator("aggettivo"),
        "avverbio": Creator("avverbio"),
    }

    def _build_tema(self,entry_data):
        qset=morph_models.Tema.objects.all()
        for arg,val in entry_data:
            qset=qset.filter(temaentry__argument__name=arg,temaentry__value__name=val)

        L_tema=list(qset)
        if L_tema:
            for t in L_tema:
                if t.temaentry_set.count() == len(entry_data): 
                    return t
        labels={}
        for k,v in entry_data[1:]:
            if k not in labels: labels[k]=[]
            labels[k].append(v)
        t=[ entry_data[0][1] ]
        for k in labels:
            val=", ".join(labels[k])
            pre=k.replace("derivato","der.")
            t.append( "%s %s" % (pre,val) )
        tema_name="; ".join(t)

        tema_obj=morph_models.Tema.objects.create(name=tema_name)
        for k,v in entry_data:
            arg,created=morph_models.TemaArgument.objects.get_or_create(name=k)
            val,created=morph_models.TemaValue.objects.get_or_create(name=v)
            t_entry=morph_models.TemaEntry.objects.create(tema=tema_obj,argument=arg,value=val)
        return tema_obj

    def post(self,request,*args,**kwargs):
        form_root=self.RootForm(prefix="root",data=request.POST)
        
        formsets=collections.OrderedDict()

        formsets["nome"]=self._formset_factory("nome")(prefix="nome",data=request.POST)
        formsets["verbo"]=self._formset_factory("verbo")(prefix="verbo",data=request.POST)
        formsets["aggettivo"]=self._formset_factory("aggettivo")(prefix="aggettivo",data=request.POST)
        formsets["avverbio"]=self._formset_factory("avverbio")(prefix="avverbio",data=request.POST)

        if not form_root.is_valid():
            context=self.get_context_data()
            context["formsets"]=formsets
            context["form_root"]=form_root
            print("form_root",request.POST)
            return render(request,self.template_name,context)

        for k in formsets:
            if not formsets[k].is_valid():
                context=self.get_context_data()
                context["formsets"]=formsets
                context["form_root"]=form_root
                print("formsets",k,request.POST)
                return render(request,self.template_name,context)

        print("form_root",form_root.cleaned_data)

        language=lang_models.Language.objects.get(name="italiano")

        root=form_root.cleaned_data["root"]
        root_part_of_speech=form_root.cleaned_data["part_of_speech"]
        root_base=form_root.cleaned_data["base"]
        root_description=base_models.Description.objects.get(name="vuota")

        tema_list=[]

        entry_data=[ ]

        for k in formsets:
            for form in formsets[k]:
                if form.cleaned_data[DELETION_FIELD_NAME]: continue
                tema=self.creators[k]( root_part_of_speech,form.cleaned_data )
                tema_list.append(tema)
                entry_data+=[ (x["argument__name"],x["value__name"]) for x in  tema.temaentry_set.all().values("argument__name","value__name") ]

        root_obj=None
        qset_root=morph_models.Root.objects.filter(root=root,language=language,part_of_speech=root_part_of_speech)
        qset_root=qset_root.filter(tema_obj__temaentry__in=morph_models.TemaEntry.objects.filter(argument__name="base",value__name=root_base) )
        if qset_root:
            root_obj=qset_root[0]
            entry_data+=[ (x["argument__name"],x["value__name"]) for x in root_obj.tema_obj.temaentry_set.exclude(argument__name="base").values("argument__name","value__name") ]
        
        entry_data=list(set(entry_data))
        tema_obj=self._build_tema([("base",root_base) ]+entry_data)

        if root_obj is None:
            root_obj=morph_models.Root.objects.create(root=root,language=language,
                                                      part_of_speech=root_part_of_speech,
                                                      description_obj=root_description,
                                                      tema_obj=tema_obj)
        root_obj.tema_obj=tema_obj
        root_obj.save()
        root_obj.update_derived()


        return redirect("/helpers/italiano/add_root/")


