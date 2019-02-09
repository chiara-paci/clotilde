from django.contrib import admin
from morphology.models import *

# admin.site.register(Tema)

# class StemAdmin(admin.ModelAdmin):
#     list_display=('__unicode__','stem','language','paradigma','part_of_speech')

# admin.site.register(Stem,StemAdmin)

# class WordAdmin(admin.ModelAdmin):
#     list_display=('word','stem','get_stem_class_string','get_morph_class_string','dict_entry','language')

# admin.site.register(Word,WordAdmin)

# class DerivationInline(admin.TabularInline):
#     model = Derivation
#     extra = 0

# class MorphologicalRuleInline(admin.TabularInline):
#     model = MorphologicalRule
#     extra = 0

# class RegexpReplacementAdmin(admin.ModelAdmin):
#     list_display=('__unicode__','pattern','replacement')
#     list_editable=('pattern','replacement')
#     inlines=[DerivationInline,MorphologicalRuleInline]

# admin.site.register(RegexpReplacement,RegexpReplacementAdmin)

# class WordCacheAdmin(admin.ModelAdmin):
#     list_display=('cache','word','scache','language')

# admin.site.register(WordCache,WordCacheAdmin)

class NotWordAdmin(admin.ModelAdmin):
    list_display=('name','word')

admin.site.register(NotWord,NotWordAdmin)

# class RootClassInline(admin.TabularInline):
#     model = Root.classifications.through
#     extra = 0

# class RootAdmin(admin.ModelAdmin):
#     save_on_top=True
#     list_display=('__unicode__','root','tema','language','part_of_speech','get_class_string')
#     list_editable=['root','tema']
#     list_filter=['tema','part_of_speech','classifications']
#     exclude=['classifications']
#     inlines=[RootClassInline]
#     actions=['clone_root']

#     def clone_root(self,request,queryset):
#         num=0
#         for root in queryset.all():
#             old_cls=root.get_classifications()
#             root.pk=None
#             root.root="(1) "+root.root
#             root.save()
#             for (cls,negate) in old_cls:
#                 RootClassification.objects.create(root=root,classification=cls,negate=negate)
#             num+=1
#         if num == 1:
#             message_bit = "1 root was"
#         else:
#             message_bit = "%d roots were" % num
#         self.message_user(request, "%s successfully cloned." % message_bit)

#     clone_root.short_description="Clone selected root"

# admin.site.register(Root,RootAdmin)

# class DerivationRootClassInline(admin.TabularInline):
#     model = Derivation.root_classifications.through
#     extra = 0
#     verbose_name = 'root classification'

# class DerivationDstClassInline(admin.TabularInline):
#     model = Derivation.dst_classifications.through
#     extra = 0
#     verbose_name = 'destination classification'

# class DerivationAdmin(admin.ModelAdmin):
#     save_on_top=True
#     list_display=('__unicode__','name','tema','paradigma','regexp','get_root_class_string','dst_part_of_speech')
#     list_editable=('name','tema')
#     #list_editable=('name','tema','paradigma')
#     # pesa rendere editabile il paradigma
#     list_filter=['dst_part_of_speech']
#     exclude=['root_classifications','dst_classifications']
#     inlines=[DerivationRootClassInline,DerivationDstClassInline]
#     actions=['clone_derivation']

#     def clone_derivation(self,request,queryset):
#         num=0
#         for der in queryset.all():
#             old_rcls=der.get_root_classifications()
#             old_dcls=der.get_dst_classifications()
#             der.pk=None
#             der.name="(1) "+der.name
#             der.save()
#             for (cls,negate) in old_rcls:
#                 DerivationRootClassification.objects.create(derivation=der,classification=cls,negate=negate)
#             for (cls,negate) in old_dcls:
#                 DerivationDstClassification.objects.create(derivation=der,classification=cls,negate=negate)
#             num+=1
#         if num == 1:
#             message_bit = "1 derivation was"
#         else:
#             message_bit = "%d derivations were" % num
#         self.message_user(request, "%s successfully cloned." % message_bit)

#     clone_derivation.short_description="Clone selected derivation"

# admin.site.register(Derivation,DerivationAdmin)

# class MorphologicalRuleClassInline(admin.TabularInline):
#     model = MorphologicalRule.classifications.through
#     extra = 0

# class ParadigmaMorphologicalRuleInline(admin.TabularInline):
#     model = Paradigma.morphologicalrule_set.through
#     extra = 0

# class MorphologicalRuleAdmin(admin.ModelAdmin):
#     save_on_top=True
#     list_display=('__unicode__','name','dict_entry','regexp','get_class_string')#,'paradigma_string')
#     #list_display=('__unicode__','name','dict_entry','regexp','get_class_string','paradigma_string')
#     list_editable=['name','dict_entry','regexp']
#     list_filter=['first_word','regexp']
#     exclude=['classifications']
#     inlines=[MorphologicalRuleClassInline,ParadigmaMorphologicalRuleInline]
#     actions=['clone_morphologicalrule']

#     def clone_morphologicalrule(self,request,queryset):
#         num=0
#         for morphologicalrule in queryset.all():
#             old_cls=morphologicalrule.get_classifications()
#             morphologicalrule.pk=None
#             t=morphologicalrule.name.split(" ")
#             morphologicalrule.name=" ".join(t[0:1]+[" (1) "]+t[1:])
#             morphologicalrule.save()
#             for (cls,negate) in old_cls:
#                 MorphologicalRuleClassification.objects.create(morphologicalrule=morphologicalrule,classification=cls,negate=negate)
#             num+=1
#         if num == 1:
#             message_bit = "1 morphological rule was"
#         else:
#             message_bit = "%d morphological rules were" % num
#         self.message_user(request, "%s successfully cloned." % message_bit)

#     clone_morphologicalrule.short_description="Clone selected morphological rule"

# admin.site.register(MorphologicalRule,MorphologicalRuleAdmin)

# class ParadigmaAdmin(admin.ModelAdmin):
#     list_display=['__unicode__','language','is_inflected','category','part_of_speech','name']
#     list_editable=['name','part_of_speech']
#     list_filter=['part_of_speech','category']
#     exclude=['morphologicalrule_set']
#     inlines=[ParadigmaMorphologicalRuleInline]
#     actions=['clone_paradigma']

#     def clone_paradigma(self,request,queryset):
#         num=0
#         for par in queryset.all():
#             old_mrs=par.morphologicalrule_set.all()
#             par.pk=None
#             par.name="(1) "+par.name
#             par.save()
#             par.morphologicalrule_set=old_mrs
#             par.save()
#             num+=1
#         if num == 1:
#             message_bit = "1 paradigma was"
#         else:
#             message_bit = "%d paradigmas were" % num
#         self.message_user(request, "%s successfully cloned." % message_bit)

#     clone_paradigma.short_description="Clone selected paradigma"

# admin.site.register(Paradigma,ParadigmaAdmin)

# class FusionSelectClassInline(admin.TabularInline):
#     model = FusionSelect.classifications.through
#     extra = 0

# class FusionSelectRuleInline(admin.TabularInline):
#     model = FusionSelectRule
#     extra = 0

# class FusionSelectAdmin(admin.ModelAdmin):
#     save_on_top=True
#     list_display=('__unicode__','name','tema','part_of_speech','get_class_string','regexp')
#     list_editable=['name','tema','regexp']
#     list_filter=['part_of_speech','classifications']
#     exclude=['classifications']
#     inlines=[FusionSelectClassInline,FusionSelectRuleInline]
#     actions=['clone_fusionselect']

#     def clone_fusionselect(self,request,queryset):
#         num=0
#         for fusionselect in queryset.all():
#             old_cls=fusionselect.get_classifications()
#             fusionselect.pk=None
#             fusionselect.name="(1) "+fusionselect.name
#             fusionselect.save()
#             for (cls,negate) in old_cls:
#                 FusionSelectClassification.objects.create(select=fusionselect,classification=cls,negate=negate)
#             num+=1
#         if num == 1:
#             message_bit = "1 fusionselect was"
#         else:
#             message_bit = "%d fusionselects were" % num
#         self.message_user(request, "%s successfully cloned." % message_bit)

#     clone_fusionselect.short_description="Clone selected fusionselect"

# admin.site.register(FusionSelect,FusionSelectAdmin)

# class FusionRuleAdmin(admin.ModelAdmin):
#     save_on_top=True
#     inlines=[FusionSelectRuleInline]
#     actions=['clone_fusionrule']

#     def clone_fusionrule(self,request,queryset):
#         num=0
#         for fusionrule in queryset.all():
#             old_sels=fusionrule.fusionselectrule_set.all()
#             fusionrule.pk=None
#             fusionrule.name="(1) "+fusionrule.name
#             fusionrule.save()
#             for sel in old_sels:
#                 FusionSelectRule.objects.create(rule=fusionrule,select=sel.select,pos=sel.pos)
#             num+=1
#         if num == 1:
#             message_bit = "1 fusionrule was"
#         else:
#             message_bit = "%d fusionrules were" % num
#         self.message_user(request, "%s successfully cloned." % message_bit)

#     clone_fusionrule.short_description="Clone selected fusion rule"

# admin.site.register(FusionRule,FusionRuleAdmin)

# class FusedWordWordInline(admin.TabularInline):
#     model = FusedWordWord
#     extra = 0

# class FusedWordAdmin(admin.ModelAdmin):
#     save_on_top=True
#     inlines=[FusedWordWordInline]

# admin.site.register(FusedWord,FusedWordAdmin)

