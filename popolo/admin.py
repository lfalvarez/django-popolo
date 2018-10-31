from django.contrib import admin
from django.forms import TextInput
from django.db import models

try:
    from django.contrib.contenttypes.admin import GenericTabularInline
except ImportError:
    from django.contrib.contenttypes.generic import GenericTabularInline

from popolo import models as popolo_models


class ClassificationAdmin(admin.ModelAdmin):
    model = popolo_models.Classification
    list_display = ('scheme', 'code', 'descr', )
    list_filter = ('scheme', )
    search_fields = ('code', 'descr', )


class RoleTypeAdmin(admin.ModelAdmin):
    model = popolo_models.RoleType
    list_display = ('label', 'classification', 'priority', 'other_label', )
    list_filter = (
        ('classification', admin.RelatedOnlyFieldListFilter),
    )
    list_select_related = ('classification', )
    search_fields = ('label', 'other_label', )

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "classification":
            kwargs["queryset"] = popolo_models.Classification.objects.filter(
                scheme='FORMA_GIURIDICA_OP'
            ).order_by('code')
        return super(RoleTypeAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)


class IdentifiersInline(GenericTabularInline):
    model = popolo_models.Identifier
    extra = 0
    max_num = 5


class OriginalEducationInline(admin.TabularInline):
    model = popolo_models.OriginalEducationLevel
    show_change_link = True
    extra = 0
    max_num = 10
    readonly_fields = ('name', )

    def has_add_permission(self, request, obj=None):
        return False


class EducationLevelAdmin(admin.ModelAdmin):
    model = popolo_models.EducationLevel
    list_display = ('name', )
    inlines = (IdentifiersInline, OriginalEducationInline, )


class OriginalEducationLevelAdmin(admin.ModelAdmin):
    model = popolo_models.OriginalEducationLevel
    list_display = ('name', 'normalized_education_level', )
    list_filter = ('normalized_education_level', )
    search_fields = ('name', 'normalized_education_level__name', )
    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size': '120'})},
    }


class OriginalProfessionInline(admin.TabularInline):
    model = popolo_models.OriginalProfession
    show_change_link = True
    extra = 0
    max_num = 10
    readonly_fields = ('name', )

    def has_add_permission(self, request, obj=None):
        return False


class ProfessionAdmin(admin.ModelAdmin):
    model = popolo_models.Profession
    list_display = ('name', )
    inlines = (IdentifiersInline, OriginalProfessionInline, )


class OriginalProfessionAdmin(admin.ModelAdmin):
    model = popolo_models.OriginalProfession
    list_display = ('name', 'normalized_profession', )
    list_filter = ('normalized_profession', )
    search_fields = ('name', 'normalized_profession__name', )
    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size': '120'})},
    }


admin.site.register(popolo_models.RoleType, RoleTypeAdmin)
admin.site.register(popolo_models.Classification, ClassificationAdmin)
admin.site.register(popolo_models.EducationLevel, EducationLevelAdmin)
admin.site.register(popolo_models.OriginalEducationLevel, OriginalEducationLevelAdmin)
admin.site.register(popolo_models.Profession, ProfessionAdmin)
admin.site.register(popolo_models.OriginalProfession, OriginalProfessionAdmin)
admin.site.register(popolo_models.Language)
