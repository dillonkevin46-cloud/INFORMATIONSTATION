from django.db import models
from django.conf import settings
import uuid

class Device(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    hostname = models.CharField(max_length=255)
    os_info = models.CharField(max_length=255, blank=True, null=True)
    public_ip = models.GenericIPAddressField(blank=True, null=True)
    local_ip = models.GenericIPAddressField(blank=True, null=True)
    mac_address = models.CharField(max_length=50, blank=True, null=True, unique=True)
    
    agent_version = models.CharField(max_length=20, blank=True, null=True)
    is_online = models.BooleanField(default=False)
    last_seen = models.DateTimeField(blank=True, null=True)
    
    # Relationships
    assigned_client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='devices')
    
    # Monitoring flags
    is_important = models.BooleanField(default=False, help_text="Alert if offline")
    
    # Specs (JSON for flexibility)
    specs = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.hostname} ({self.local_ip})"

class NetworkInterface(models.Model):
    device = models.ForeignKey(Device, related_name='interfaces', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    mac_address = models.CharField(max_length=50)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

class TelemetryData(models.Model):
    device = models.ForeignKey(Device, related_name='telemetry', on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    cpu_usage = models.FloatField(help_text="Percentage")
    ram_usage = models.FloatField(help_text="Percentage")
    disk_usage = models.FloatField(help_text="Percentage")
    
    class Meta:
        ordering = ['-timestamp']

class Asset(models.Model):
    """
    Non-Agent Assets (Printers, Switches, Monitors, etc.)
    """
    CATEGORY_CHOICES = (
        ('printer', 'Printer'),
        ('switch', 'Switch/Router'),
        ('monitor', 'Monitor'),
        ('mobile', 'Mobile Device'),
        ('other', 'Other'),
    )
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    is_monitored = models.BooleanField(default=False)
    
    assigned_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='assets', on_delete=models.SET_NULL, null=True, blank=True)
    purchase_date = models.DateField(blank=True, null=True)
    warranty_expiry = models.DateField(blank=True, null=True)
    notes = models.TextField(blank=True)
    
    specs = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"{self.name} ({self.category})"

class MonitoringAlert(models.Model):
    SEVERITY_CHOICES = (
        ('info', 'Info'),
        ('warning', 'Warning'),
        ('critical', 'Critical'),
    )
    device = models.ForeignKey(Device, related_name='alerts', on_delete=models.CASCADE, null=True, blank=True)
    asset = models.ForeignKey(Asset, related_name='alerts', on_delete=models.CASCADE, null=True, blank=True)
    
    message = models.TextField()
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='info')
    created_at = models.DateTimeField(auto_now_add=True)
    resolved = models.BooleanField(default=False)
    resolved_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Alert: {self.message} ({self.severity})"
