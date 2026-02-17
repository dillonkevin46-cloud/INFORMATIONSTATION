from rest_framework import viewsets
from .models import Device
from .serializers import DeviceSerializer

class DeviceViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows devices to be viewed or edited.
    """
    # Optimized to fix N+1 query issue for telemetry data
    queryset = Device.objects.all().prefetch_related('telemetry').order_by('-created_at')
    serializer_class = DeviceSerializer
