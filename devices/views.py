from rest_framework import viewsets
from .models import Device
from .serializers import DeviceSerializer

class DeviceViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows devices to be viewed or edited.
    """
    queryset = Device.objects.all().order_by('-created_at')
    serializer_class = DeviceSerializer
