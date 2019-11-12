from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.db.models import Q

import collections

from . import models

class InitialFilter(admin.SimpleListFilter):
    title = "initial"
    parameter_name = 'initial'
    field = ""

    def lookups(self, request, model_admin):

        qset=model_admin.get_queryset(request)
        initial_list=[ x[self.field][0] for x in qset.values(self.field) ]
        initial_list=list(set(initial_list))
        initial_list.sort()
        
        return [ (x,x) for x in initial_list ]

    def queryset(self, request, queryset):
        if self.value():
            kwargs={
                self.field+"__startswith": self.value()
            }
            return queryset.filter(**kwargs)
        return queryset

def initial_filter_factory(sel_field):
    class FieldInitialFilter(InitialFilter):
        field=sel_field
    return FieldInitialFilter

def select_filter_decorator(cls):
    class DecoratedFilter(cls):
        template = "admin/selectfilter.html"
    return DecoratedFilter

class InputListFilter(admin.SimpleListFilter):
    # title = "derivation"
    # parameter_name = 'derivation'
    # filter_key = 'derivation__name__icontains'
    template = "admin/inputfilter.html"

    def has_output(self):
        return True

    def choices(self, changelist):
        yield {
            'selected': self.value() is None,
            'query_string': changelist.get_query_string(remove=[self.parameter_name]),
            'display': _('All'),
            "all": True,
        }
        for lookup, title in self.lookup_choices:
            yield {
                'selected': self.value() == str(lookup),
                'query_string': changelist.get_query_string({self.parameter_name: lookup}),
                'display': title,
                "all": False,
                "parameter": self.parameter_name,
            }

    def lookups(self, request, model_admin):
        return [ (self.value(),self.value()) ]

    def queryset(self, request, queryset):
        if not self.value():
            return queryset
        kwargs={
            self.filter_key: self.value()
        }
        return queryset.filter(**kwargs)

class DescriptionEntryListFilter(admin.SimpleListFilter):
    title = "description entry"
    parameter_name = 'description_entry'
    template = "admin/descriptionentryfilter.html"
    field_name = 'description_obj'

    def has_output(self):
        return True

    def choices(self, changelist):
        yield {
            'selected': not bool(self.value()),
            'query_string': changelist.get_query_string(remove=[self.parameter_name]),
            'display': _('Reset'),
            "type": "all",
        }

        choices_sel,choices=self.lookup_choices

        print(choices_sel)

        for key_sel,val_sel in choices_sel:
            T={
                "keys": key_sel,
                "vals": val_sel,
                "type": "selected",
            }
            
            yield T

        for lookup, title, vals in choices:
            T={
                "lookup": str(lookup),
                'display': title,
                "type": "choice",
                "values": vals,
            }
            yield T

    def lookups(self, request, model_admin):
        def flabel(D):
            if D["invert"]:
                D["x"]="!"
            else:
                D["x"]=""
            return "%(x)s%(value__string)s" % D

        def fkey(D):
            if D["invert"]:
                D["x"]="1"
            else:
                D["x"]="0"
            return "%(value__pk)s:%(x)s" % D
            

        qset=models.Entry.objects.all().values("attribute__pk","attribute__name",
                                               "value__pk","value__string",
                                               "invert").distinct()

        keys=list( set([ (e["attribute__name"],e["attribute__pk"]) for e in qset ]) )
        keys.sort()
        ret_d=collections.OrderedDict([ (k,[]) for k in keys ])        
        
        for e in qset:
            key=(e["attribute__name"],e["attribute__pk"])
            ret_d[key].append( (e["value__string"],e["invert"],e["value__pk"],fkey(e),flabel(e)) )

        ret=[]
        for k_name,k_pk in ret_d:
            ret_d[ (k_name,k_pk) ].sort()
            ret.append( (str(k_pk),k_name,
                         [ (v_key,v_label) for v_str,v_inv,v_pk,v_key,v_label in ret_d[ (k_name,k_pk) ] ]) )

        if not self.value():
            return [],ret

        qfilter=Q()
        for arg,val,inv in self.value():
            qfilter=qfilter|Q(attribute__pk=arg,value__pk=val,invert=inv)
        qset=models.Entry.objects.filter(qfilter)

        ret_sel=[]
        for e in qset:
            print(e)
            key_sel=[ (str(k_pk),k_name,k_pk==e.attribute.pk) for k_name,k_pk in keys ]
            k=( e.attribute.name, e.attribute.pk )
            val_sel=[ (v_key,v_label, (v_pk==e.value.pk) ) for v_str,v_inv,v_pk,v_key,v_label in ret_d[k] ]
            ret_sel.append( (key_sel,val_sel) )
            
        return ret_sel,ret

    def value(self):
        """
        Return the value (in string format) provided in the request's
        query string for this filter, if any, or None if the value wasn't
        provided.
        """
        vals=self.used_parameters.get(self.parameter_name)
        if not vals: return []
        t_entry=vals.split("_")
        ret=[]
        for e in t_entry:
            t=e.split(":")
            arg=int(t[0])
            val=int(t[1])
            inv=(int(t[2])==1)
            ret.append( (arg,val,inv) )
        return ret

    def queryset(self, request, queryset):
        vals=self.value()
        print(vals)
        if not vals: return queryset
        qset=models.Description.objects.all()
        for arg,val,inv in vals:
            qset=qset.filter(entries__attribute__pk=arg,
                             entries__value__pk=val,
                             entries__invert=inv)

        kwargs={
            self.field_name+"__in": qset
        }
        return queryset.filter(**kwargs)

    
######################################

admin.site.register(models.CasePair)

class CasePairInline(admin.TabularInline):
    model = models.CaseSet.pairs.through
    extra = 0

class CaseSetAdmin(admin.ModelAdmin):
    list_display=['name','length']
    inlines=[CasePairInline]
    fields=['name']

admin.site.register(models.CaseSet,CaseSetAdmin)

class TokenRegexpAdmin(admin.ModelAdmin):
    list_display=['name','regexp',"count_set"]
    list_editable=['regexp']

admin.site.register(models.TokenRegexp,TokenRegexpAdmin)

class AlphabeticOrderAdmin(admin.ModelAdmin):
    list_display=['name','order']
    list_editable=['order']

admin.site.register(models.AlphabeticOrder,AlphabeticOrderAdmin)

class TokenRegexpSetThroughAdmin(admin.ModelAdmin):
    list_display=['__str__','token_regexp_set','order','token_regexp','regexp','bg_color','fg_color','disabled']
    list_editable=['order','token_regexp','bg_color','fg_color','disabled']

    list_filter=["token_regexp_set"]

admin.site.register(models.TokenRegexpSetThrough,TokenRegexpSetThroughAdmin)

class TokenRegexpInline(admin.TabularInline):
    model = models.TokenRegexpSet.regexps.through
    extra = 0

class TokenRegexpSetAdmin(admin.ModelAdmin):
    list_display=['name','regexp_all']
    inlines = [TokenRegexpInline]

admin.site.register(models.TokenRegexpSet,TokenRegexpSetAdmin)

class DescriptionEntryInline(admin.TabularInline):
    model = models.Description.entries.through
    extra = 0

class DescriptionAdmin(admin.ModelAdmin):
    exclude = [ "entries" ] 
    inlines=[DescriptionEntryInline] 
    list_display=[ "__str__","name","count_references",
                   "count_fusionrules",
                   "count_inflections",
                   "count_derivations",
                   "_build" ]
    list_editable=["name"]
    save_as=True

    def _build(self,obj):
        return "[%s]" % obj.build()

    def count_fusionrules(self,obj): return obj.fusionrule_set.count()
    def count_inflections(self,obj): return obj.inflection_set.count()
    def count_derivations(self,obj): return obj.derivation_set.count()

    def count_references(self,obj):
        M=0
        for f in obj._meta.get_fields():
            if not f.auto_created: continue
            if not f.is_relation: continue
            if f.concrete: continue
            kwargs={
                 f.remote_field.name: obj
            }
            M+=f.related_model.objects.filter(**kwargs).count()
        return M
    
admin.site.register(models.Description,DescriptionAdmin)

class EntryAdmin(admin.ModelAdmin):
    inlines=[DescriptionEntryInline]
    list_display = ["__str__","description_count","invert","attribute","value","value_id"]
    list_editable = ["value"]

    def value_id(self,obj): return obj.value.pk

    def description_count(self,obj):
        return obj.description_set.count()

admin.site.register(models.Entry,EntryAdmin)

class EntryInline(admin.TabularInline):
    model = models.Entry
    extra = 0

class ValueAdmin(admin.ModelAdmin):
    inlines = [EntryInline]
    list_display=["__str__","string","order","attributes","entry_count"]
    list_editable=["string","order"]

    def entry_count(self,obj):
        return obj.entry_set.count()

    def attributes(self,obj):
        return ",".join([a["attribute__name"] for a in models.Entry.objects.filter(value=obj).values("attribute__name").distinct()])
    
admin.site.register(models.Value,ValueAdmin)

class AttributeAdmin(admin.ModelAdmin):
    inlines = [EntryInline]
    list_display=["__str__","name","order","entry_count"]
    list_editable=["name","order"]
    

    def entry_count(self,obj):
        return obj.entry_set.count()

admin.site.register(models.Attribute,AttributeAdmin)
    
