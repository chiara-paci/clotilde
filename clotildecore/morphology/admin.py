from django.contrib import admin
from django import forms
from django.db.models.query import QuerySet,Q
from django.db.models import Count
from django.utils.html import format_html

from . import models
from base import models as base_models
from base import admin as base_admin
from languages import models as lang_models

DEFAULT_LANGUAGE= lang_models.Language.objects.get(name="italiano")
DEFAULT_DESCRIPTION = base_models.Description.objects.get(name="vuota")
DEFAULT_REGSUB = models.RegexpReplacement.objects.get(pattern="(.+)",replacement="\\1")

def build_static_iterator(obj_list):
    class ModelChoiceIterator:
        def __init__(self, field):
            self.field = field
            self._object_list=obj_list
            if self.field.empty_label is not None:
                self._ind=-2
            else:
                self._ind=-1

        def __next__(self):
            self._ind+=1
            if self._ind<0: return ("", self.field.empty_label)
            if self._ind >= len(self._object_list): raise StopIteration()
            return self.choice( self._object_list[self._ind] )

        def __iter__(self): return type(self)(self.field)

        def __len__(self):
            return len(self._object_list) + (1 if self.field.empty_label is not None else 0)

        def __bool__(self):
            return self.field.empty_label is not None or len(self._object_list)!=0

        def choice(self, obj):
            return (self.field.prepare_value(obj), self.field.label_from_instance(obj))

    return ModelChoiceIterator

admin.site.register(models.FusionRuleRelation)

class TemaEntryInline(admin.TabularInline):
    model = models.TemaEntry
    extra = 0

class TemaArgumentAdmin(admin.ModelAdmin):
    inlines = [TemaEntryInline]
    list_display=["__str__","name","num_entries"]

admin.site.register(models.TemaArgument,TemaArgumentAdmin)

class TemaValueReferenceFilter(admin.SimpleListFilter):

    title = "reference"
    parameter_name = 'ref'

    def lookups(self, request, model_admin):
        return [
            ( "notema","no tema"),
            ( "noref","no reference"),
            ( "derivation_only","derivation only"),
            ( "root_only","root only"),
            ( "fusion_rule_only","fusion rule only"),
            ( "derivation","with derivation"),
            ( "root","with root"),
            ( "fusion_rule","with fusion rule"),
            ( "mixed","mixed"),
        ]

    def _tema_queryset(self,val):
        qset=models.Tema.objects.all().annotate(num_der=Count("derivation"),
                                                num_root=Count("root"),
                                                num_frule=Count("fusionrule"))
        if val=="noref":
            return qset.filter(num_der=0,num_root=0,num_frule=0)
        if val=="derivation_only":
            return qset.filter(num_root=0,num_frule=0).exclude(num_der=0)
        if val=="root_only":
            return qset.filter(num_der=0,num_frule=0).exclude(num_root=0)
        if val=="fusion_rule_only":
            return qset.filter(num_root=0,num_der=0).exclude(num_frule=0)
        if val=="derivation":
            return qset.exclude(num_der=0)
        if val=="root":
            return qset.exclude(num_root=0)
        if val=="fusion_rule":
            return qset.exclude(num_frule=0)
        qset=qset.exclude(num_der=0,num_root=0,num_frule=0)
        qset=qset.exclude(num_der=0,num_root=0)
        qset=qset.exclude(num_der=0,num_frule=0)
        qset=qset.exclude(num_root=0,num_frule=0)
        return qset
        
    
    def queryset(self, request, queryset):
        val=self.value()
        if not val: return queryset
        if val=="notema":
            return queryset.all().annotate(num_tema=Count("temaentry")).filter(num_tema=0)
        
        tqset=self._tema_queryset(val)
        return queryset.filter(temaentry__tema__in=tqset).distinct()

class TemaValueAdmin(admin.ModelAdmin):
    list_display=["__str__","name","num_entries","temas"]
    list_editable=["name"]
    inlines = [TemaEntryInline]
    list_filter=[TemaValueReferenceFilter]

admin.site.register(models.TemaValue,TemaValueAdmin)

class DerivationFormSet(forms.models.BaseInlineFormSet):
    @property
    def empty_form(self):
       form = super(DerivationFormSet, self).empty_form
       form.fields['language'].initial = DEFAULT_LANGUAGE
       form.fields['regsub'].initial = DEFAULT_REGSUB
       form.fields['description_obj'].initial = DEFAULT_DESCRIPTION
       form.fields['root_description_obj'].initial = DEFAULT_DESCRIPTION
       return form

class DerivationInline(admin.TabularInline):
    model = models.Derivation
    extra = 0
    formset = DerivationFormSet

class RootFormSet(forms.models.BaseInlineFormSet):
    @property
    def empty_form(self):
       form = super(RootFormSet, self).empty_form
       form.fields['language'].initial = DEFAULT_LANGUAGE
       form.fields['description_obj'].initial = DEFAULT_DESCRIPTION
       return form

class RootInline(admin.TabularInline):
    model = models.Root
    extra = 0
    formset = RootFormSet
    
class StemInline(admin.TabularInline):
    model = models.Stem
    extra = 0
    
class FusionRuleInline(admin.TabularInline):
    model = models.FusionRule
    extra = 0

class TemaNameListFilter(admin.SimpleListFilter):
    title = "name"
    parameter_name = 'prefix'

    def lookups(self, request, model_admin):
        def label(s):
            s=s.replace(";"," ")
            t=s.split()
            if len(t)==1: return s
            base=t[0]
            if t[1] in ["derivato","proprio","derivata"]:
                return base+" "+t[1]
            return base

        name_list=[ label(x["name"]) for x in models.Tema.objects.all().values("name") ] 
        name_list=list(set(name_list))
        name_list.sort()
        
        return [ (x,x) for x in name_list ]

    def queryset(self, request, queryset):
        val=self.value()
        if not val: return queryset
        return queryset.filter(name__startswith=val)

class TemaEntryFilter(admin.SimpleListFilter):
    title = "entry"
    parameter_name = 'argval'

    def lookups(self, request, model_admin):
        def label(s):
            s=s.replace(";"," ")
            t=s.split()
            if len(t)==1: return s
            base=t[0]
            if t[1] in ["derivato","proprio"]:
                return base+" "+t[1]
            return base

        qset=models.TemaEntry.objects.all().values("argument__pk","argument__name",
                                                   "value__pk","value__name").distinct()
        
        name_list=[ (
            "%(argument__pk)s_%(value__pk)s" % k,
            "%(argument__name)s=%(value__name)s" % k
        ) for k in qset ]
         
        return name_list

    def queryset(self, request, queryset):
        val=self.value()
        print(val)
        if not val: return queryset

        t=val.split("_")
        arg=int(t[0])
        val=int(t[1])
        print(arg,val)
        qset=[ x["tema__pk"] for x in models.TemaEntry.objects.filter(argument__pk=arg,
                                                                      value__pk=val).values("tema__pk") ]
        
        return queryset.filter(pk__in=qset)

class TemaReferenceFilter(admin.SimpleListFilter):

    title = "reference"
    parameter_name = 'ref'

    def lookups(self, request, model_admin):
        return [
            ( "noref","no references"),
            ( "derivation_only","derivation only"),
            ( "root_only","root only"),
            ( "fusion_rule_only","fusion rule only"),
            ( "derivation","with derivation"),
            ( "root","with root"),
            ( "fusion_rule","with fusion rule"),
            ( "mixed","mixed"),
        ]

    def queryset(self, request, queryset):
        val=self.value()
        if not val: return queryset
        qset=queryset.annotate(num_der=Count("derivation"),
                               num_root=Count("root"),
                               num_frule=Count("fusionrule"))
        if val=="noref":
            return qset.filter(num_der=0,num_root=0,num_frule=0)
        if val=="derivation_only":
            return qset.filter(num_root=0,num_frule=0).exclude(num_der=0)
        if val=="root_only":
            return qset.filter(num_der=0,num_frule=0).exclude(num_root=0)
        if val=="fusion_rule_only":
            return qset.filter(num_root=0,num_der=0).exclude(num_frule=0)
        if val=="derivation":
            return qset.exclude(num_der=0)
        if val=="root":
            return qset.exclude(num_root=0)
        if val=="fusion_rule":
            return qset.exclude(num_frule=0)
        qset=qset.exclude(num_der=0,num_root=0,num_frule=0)
        qset=qset.exclude(num_der=0,num_root=0)
        qset=qset.exclude(num_der=0,num_frule=0)
        qset=qset.exclude(num_root=0,num_frule=0)
        return qset
        
class TemaAdmin(admin.ModelAdmin):
    inlines=[TemaEntryInline,DerivationInline,RootInline,FusionRuleInline]
    list_display=[ "id","name","build",
                   "num_references","derivations",
                   "num_roots","num_derivations","num_fusion_rules" ]
    save_as=True
    list_filter=[TemaReferenceFilter,TemaNameListFilter,TemaEntryFilter]
    list_editable=["name"]

admin.site.register(models.Tema,TemaAdmin)


class TemaEntryAdmin(admin.ModelAdmin):
    list_display=["__str__","tema"]
    list_filter=["argument","value"]

admin.site.register(models.TemaEntry,TemaEntryAdmin)

class StemAdmin(admin.ModelAdmin):
    list_display=["stem","part_of_speech","root","derivation","tema","paradigma"]
    list_filter=[base_admin.initial_filter_factory("cache")]

admin.site.register(models.Stem,StemAdmin)

        
class ParadigmaInflectionInline(admin.TabularInline):
    model = models.Paradigma.inflections.through
    extra = 0

    def __init__(self,*args,**kwargs):
        obj_list=list(models.Inflection.objects.all().select_related())
        self._inflection_iterator=build_static_iterator(obj_list)
        admin.TabularInline.__init__(self,*args,**kwargs)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        field=super().formfield_for_foreignkey(db_field, request, **kwargs)
        if db_field.name == "inflection":
            field.iterator=self._inflection_iterator
        return field

class ParadigmaAdmin(admin.ModelAdmin):
    list_display=["__str__","name","part_of_speech",
                  "count_inflections",
                  "count_derivations","count_roots","count_stems","count_words"]
    list_filter=["part_of_speech"]
    list_editable=["name","part_of_speech"]
    inlines=[DerivationInline,ParadigmaInflectionInline]
    exclude=["inflections"]
    save_as=True

admin.site.register(models.Paradigma,ParadigmaAdmin)

class PartOfSpeechAdmin(admin.ModelAdmin):
    list_display=[ "name","example","bg_color","fg_color" ]
    list_editable=[ "bg_color","fg_color" ]

    def example(self,obj):
        return format_html('<span style="background-color:%s;color:%s">%s</span>' % (obj.bg_color,obj.fg_color,obj.name))
    #example.allow_tags = True

admin.site.register(models.PartOfSpeech,PartOfSpeechAdmin)

class WordAdmin(admin.ModelAdmin):
    list_display=["cache","dict_entry","part_of_speech","stem","tema","paradigma","description"]
    list_filter=[base_admin.initial_filter_factory("cache")]
    
admin.site.register(models.Word,WordAdmin)


class WordInline(admin.TabularInline):
    model = models.Word
    extra = 0

class InflectionPartOfSpeechFilter(admin.SimpleListFilter):
    title = "part of speech"
    parameter_name = 'pos'

    def lookups(self, request, model_admin):
        def label(s):
            s=s.replace(";"," ")
            t=s.split()
            if len(t)==1: return s
            base=t[0]
            if t[1] in ["derivato","proprio"]:
                return base+" "+t[1]
            return base

        qset=models.PartOfSpeech.objects.all().values("pk","name").distinct()
        
        name_list=[ (
            "%(pk)s" % k,
            "%(name)s" % k
        ) for k in qset ]
         
        return name_list

    def queryset(self, request, queryset):
        val=self.value()
        print(val)
        if not val: return queryset
        pk=int(val)
        return queryset.filter(paradigma__part_of_speech=pk).distinct()

class InflectionAdmin(admin.ModelAdmin):
    list_filter=["dict_entry",InflectionPartOfSpeechFilter,"paradigma","description_obj"]
    list_display=["regsub","dict_entry","num_paradigmas","description_obj","description"]
    list_editable=["description_obj"]
    inlines=[ParadigmaInflectionInline] #,WordInline]
    save_as=True

admin.site.register(models.Inflection,InflectionAdmin)

class DerivationNameListFilter(admin.SimpleListFilter):
    title = "name"
    parameter_name = 'prefix'

    def lookups(self, request, model_admin):
        def label(s):
            s=s.replace(";"," ")
            t=s.split()
            if len(t)==1: return s
            base=t[0]
            if t[1] in ["derivato","proprio"]:
                return base+" "+t[1]
            return base

        name_list=[ label(x["name"]) for x in models.Derivation.objects.all().values("name") ] 
        name_list=list(set(name_list))
        name_list.sort()
        
        return [ (x,x) for x in name_list ]

    def queryset(self, request, queryset):
        val=self.value()
        if not val: return queryset
        return queryset.filter(name__startswith=val)

class DerivationDescriptionEntryFilter(admin.SimpleListFilter):
    title = "description entry"
    parameter_name = 'descentry'

    def lookups(self, request, model_admin):
        def label(D):
            if D["invert"]:
                D["x"]="!"
            else:
                D["x"]=""
            return "%(attribute__name)s=%(x)s%(value__string)s" % D

        def key(D):
            if D["invert"]:
                D["x"]="1"
            else:
                D["x"]="0"
            return "%(attribute__pk)s_%(value__pk)s_%(x)s" % D
            

        qset=base_models.Entry.objects.all().values("attribute__pk","attribute__name",
                                                    "value__pk","value__string",
                                                    "invert").distinct()
        
        name_list=[ (key(k),label(k)) for k in qset ]
         
        return name_list

    def queryset(self, request, queryset):
        val=self.value()
        print(val)
        if not val: return queryset

        t=val.split("_")
        arg=int(t[0])
        val=int(t[1])
        inv=(int(t[2])==1)
        print(arg,val,inv)
        qset=base_models.Description.objects.filter(entries__attribute__pk=arg,
                                                    entries__value__pk=val,
                                                    entries__invert=inv).distinct()
        return queryset.filter(description_obj__in=qset)
    

class DerivationAdmin(admin.ModelAdmin):
    list_display = [ "__str__",
                     "regsub","root_part_of_speech","name","paradigma",
                     "num_stem",
                     "description_obj",
                     "tema",
                     "root_description", 
                     "paradigma",
                     "tema_obj",
                     "part_of_speech" ]
    list_filter = [ "root_part_of_speech",
                    "regsub__pattern",
                    DerivationNameListFilter,
                    DerivationDescriptionEntryFilter,
                    ('paradigma', admin.RelatedOnlyFieldListFilter),
                    "tema_obj"]
    list_editable = [ "name" ]#,"description_obj" ]
    save_as=True
    inlines=[StemInline]

admin.site.register(models.Derivation,DerivationAdmin)


class RootAdmin(admin.ModelAdmin):
    save_as=True
    list_filter=["part_of_speech",base_admin.initial_filter_factory("root")]
    list_display=["root","language","part_of_speech","tema_obj","description_obj"]
    inlines=[StemInline]
    list_editable=["description_obj"] #,"tema_obj","part_of_speech"]

    def get_form(self, request, obj=None, **kwargs):
        form = super(RootAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['language'].initial = DEFAULT_LANGUAGE
        form.base_fields['description_obj'].initial = DEFAULT_DESCRIPTION
        return form

admin.site.register(models.Root,RootAdmin)

class FusionRuleRelationInline(admin.TabularInline):
    model = models.FusionRuleRelation
    extra = 0

class FusionAdmin(admin.ModelAdmin): 
    inlines=[FusionRuleRelationInline]
    save_as=True

admin.site.register(models.Fusion,FusionAdmin)

class FusionRuleAdmin(admin.ModelAdmin): 
    inlines=[FusionRuleRelationInline]
    save_as=True
    list_display=[ "name","description", "description_obj","num_fusions", "tema","part_of_speech", "regsub" ]
    list_editable=["description_obj"]
    list_filter=["part_of_speech"]

admin.site.register(models.FusionRule,FusionRuleAdmin)

class FusedWordRelationInline(admin.TabularInline):
    model = models.FusedWordRelation
    extra = 0

class FusedWordAdmin(admin.ModelAdmin):
    list_display = [ "cache", "fusion" ]
    inlines = [FusedWordRelationInline]
    list_filter=[base_admin.initial_filter_factory("cache"),"fusion"]

admin.site.register(models.FusedWord,FusedWordAdmin)
admin.site.register(models.FusedWordRelation)

class InflectionInline(admin.TabularInline):
    model = models.Inflection
    extra = 0

class RegexpReplacementAdmin(admin.ModelAdmin):
    list_display = [ "__str__","num_fusion_rules",
                     "num_derivations","num_inflections", "pattern", "replacement", "reverse" ]
    list_editable = [ "pattern", "replacement" ]
    list_filter = [ "pattern", "replacement" ]
    inlines=[InflectionInline,DerivationInline,FusionRuleInline]

    def get_form(self, request, obj=None, **kwargs):
        form = super(RegexpReplacementAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['pattern'].initial = '(.+)'
        form.base_fields['replacement'].initial = '\\1'
        return form

admin.site.register(models.RegexpReplacement,RegexpReplacementAdmin)


class RegexpReverseAdmin(admin.ModelAdmin):
    list_display = [ "__str__", "target", "pattern", "replacement" ]
    list_editable = [ "pattern", "replacement" ]
    #list_filter = [ "pattern", "replacement" ]

    def get_form(self, request, obj=None, **kwargs):
        form = super(RegexpReverseAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['pattern'].initial = '(.+)'
        form.base_fields['replacement'].initial = '\\1'
        return form

admin.site.register(models.RegexpReverse,RegexpReverseAdmin)

