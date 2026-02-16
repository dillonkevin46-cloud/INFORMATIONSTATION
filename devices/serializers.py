from rest_framework import serializers
from .models import Device, TelemetryData

class TelemetrySerializer(serializers.ModelSerializer):
    class Meta:
        model = TelemetryData
        fields = ['timestamp', 'cpu_usage', 'ram_usage', 'disk_usage']

class DeviceSerializer(serializers.ModelSerializer):
    telemetry = TelemetrySerializer(many=True, read_only=True, source='telemetry.all')
    
    class Meta:
        model = Device
        fields = '__all__'
