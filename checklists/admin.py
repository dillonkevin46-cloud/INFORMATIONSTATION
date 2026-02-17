from django.contrib import admin
from .models import FormTemplate, FormSubmission

@admin.register(FormTemplate)
class FormTemplateAdmin(admin.ModelAdmin):
    list_display = ('title', 'form_type', 'updated_at')
    list_filter = ('form_type',)

@admin.register(FormSubmission)
class FormSubmissionAdmin(admin.ModelAdmin):
    list_display = ('template', 'submitted_by', 'completed', 'submitted_at')
    list_filter = ('completed', 'template__form_type')
    readonly_fields = ('submitted_at',)
