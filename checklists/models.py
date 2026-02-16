from django.db import models
from django.conf import settings
from tickets.models import Ticket

class FormTemplate(models.Model):
    FORM_TYPES = (
        ('checklist', 'Checklist'),
        ('onboarding', 'Onboarding'),
        ('offboarding', 'Offboarding'),
        ('handover', 'Device Handover'),
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    form_type = models.CharField(max_length=50, choices=FORM_TYPES, default='checklist')

    # Structure: [{'label': 'Is PC working?', 'type': 'checkbox', 'required': True}, ...]
    fields = models.JSONField(default=list, help_text="List of field definitions")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class FormSubmission(models.Model):
    template = models.ForeignKey(FormTemplate, related_name='submissions', on_delete=models.CASCADE)
    submitted_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='submissions', on_delete=models.SET_NULL, null=True)
    ticket = models.ForeignKey(Ticket, related_name='forms', on_delete=models.SET_NULL, null=True, blank=True)

    # Structure: {'field_1': True, 'field_2': 'Some text'}
    data = models.JSONField(default=dict)

    completed = models.BooleanField(default=False)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.template.title} - {self.submitted_by}"
