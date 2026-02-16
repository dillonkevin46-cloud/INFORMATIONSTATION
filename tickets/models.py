from django.db import models
from django.conf import settings
from devices.models import Device

class Ticket(models.Model):
    STATUS_CHOICES = (
        ('new', 'New'),
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    )
    PRIORITY_CHOICES = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    )

    title = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    category = models.CharField(max_length=100, blank=True)

    client = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='tickets_created', on_delete=models.CASCADE)
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='tickets_assigned', on_delete=models.SET_NULL, null=True, blank=True)
    device = models.ForeignKey(Device, related_name='tickets', on_delete=models.SET_NULL, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    closed_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"#{self.id} - {self.title}"

class TicketMessage(models.Model):
    ticket = models.ForeignKey(Ticket, related_name='messages', on_delete=models.CASCADE)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='messages', on_delete=models.CASCADE)
    content = models.TextField()
    is_internal = models.BooleanField(default=False, help_text="If true, not visible to client")
    created_at = models.DateTimeField(auto_now_add=True)

class TimeEntry(models.Model):
    ticket = models.ForeignKey(Ticket, related_name='time_entries', on_delete=models.CASCADE)
    staff = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='time_entries', on_delete=models.CASCADE)
    description = models.TextField(blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(blank=True, null=True)
    duration_minutes = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
