from django.contrib import admin
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
    list_display=['name','regexp',"set_number"]
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

# class LanguageAdmin(admin.ModelAdmin):
#     list_display=['name','has_case','case_set','token_regexp_set','token_regexp_expression']
#     list_editable=['case_set','token_regexp_set']

# admin.site.register(models.Language,LanguageAdmin)

# class NotWordAdmin(admin.ModelAdmin):
#     list_display=('name','word')

# admin.site.register(models.NotWord,NotWordAdmin)

admin.site.register(models.SubDescription)

class DescriptionEntryInline(admin.TabularInline):
    model = models.Description.entries.through
    extra = 0

class DescriptionSubDescriptionInline(admin.TabularInline):
    model = models.Description.subdescriptions.through
    extra = 0

class DescriptionAdmin(admin.ModelAdmin):
    exclude = [ "entries","subdescriptions"]
    inlines=[DescriptionEntryInline,DescriptionSubDescriptionInline]
    list_display=[ "__str__","name","_build","count_references",
                   "count_fusionrules","count_roots","count_inflections","count_derivations","count_root_derivations" ]
    list_editable=["name"]
    save_as=True

    def _build(self,obj):
        return "[%s]" % obj.build()

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
    
