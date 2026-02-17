from django.contrib import admin
from .models import Device, Asset, MonitoringAlert, TelemetryData, NetworkInterface

@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ('hostname', 'local_ip', 'public_ip', 'agent_version', 'is_online', 'last_seen')
    list_filter = ('is_online', 'agent_version')
    search_fields = ('hostname', 'local_ip', 'mac_address')

@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'assigned_user', 'is_monitored')
    list_filter = ('category', 'is_monitored')
    search_fields = ('name',)

@admin.register(MonitoringAlert)
class MonitoringAlertAdmin(admin.ModelAdmin):
    list_display = ('device', 'message', 'severity', 'created_at', 'resolved')
    list_filter = ('severity', 'resolved')
    readonly_fields = ('created_at',)

@admin.register(TelemetryData)
class TelemetryDataAdmin(admin.ModelAdmin):
    list_display = ('device', 'cpu_usage', 'ram_usage', 'disk_usage', 'timestamp')
    list_filter = ('device',)
    readonly_fields = ('timestamp', 'device', 'cpu_usage', 'ram_usage', 'disk_usage')

@admin.register(NetworkInterface)
class NetworkInterfaceAdmin(admin.ModelAdmin):
    list_display = ('device', 'name', 'ip_address', 'mac_address', 'is_active')
