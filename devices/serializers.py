from rest_framework import serializers
from .models import Device, TelemetryData

class TelemetrySerializer(serializers.ModelSerializer):
    class Meta:
        model = TelemetryData
        fields = ['timestamp', 'cpu_usage', 'ram_usage', 'disk_usage']

class DeviceSerializer(serializers.ModelSerializer):
    # Optimized: Limit telemetry data to the latest 10 records to reduce payload size.
    # Uses SerializerMethodField which works efficiently with prefetched data.
    telemetry = serializers.SerializerMethodField()
    
    class Meta:
        model = Device
        fields = '__all__'

    def get_telemetry(self, obj):
        # obj.telemetry.all() leverages prefetch_related if called in the viewset
        return TelemetrySerializer(obj.telemetry.all()[:10], many=True).data
