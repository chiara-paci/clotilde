from django.shortcuts import render
from django.utils.translation import ugettext as _

from django.views.generic import TemplateView,DetailView,View
from django.views.generic.detail import SingleObjectMixin
from django import forms
from django.shortcuts import render,redirect
from django.urls import reverse
from django.forms.formsets import  ORDERING_FIELD_NAME,DELETION_FIELD_NAME

import collections

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
                    normal_row='<td>%(label)s</td><td>%(errors)s%(field)s%(help_text)s</td>',
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
        pattern = forms.CharField(initial="(.+)")
        replacement = forms.CharField(initial=r"\1")
        person = forms.ChoiceField( choices=[( "prima singolare", "prima singolare" ),
                                             ( "seconda singolare", "seconda singolare" ),
                                             ( "terza singolare", "terza singolare" ),
                                             ( "prima plurale", "prima plurale" ),
                                             ( "seconda plurale", "seconda plurale" ),
                                             ( "terza plurale", "terza plurale" )] )

    class InfiniteForm(forms.Form):
        pattern = forms.CharField(initial="(.+)")
        replacement = forms.CharField(initial=r"\1")

    class ParticipeForm(forms.Form):
        pattern = forms.CharField(initial="(.+)")
        replacement = forms.CharField(initial=r"\1")
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
