from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets
from .models import Device
from .serializers import DeviceSerializer

# API ViewSet
class DeviceViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows devices to be viewed or edited.
    """
    queryset = Device.objects.all().order_by('-created_at')
    serializer_class = DeviceSerializer

# Standard Views
def device_list(request):
    devices = Device.objects.all().order_by('-last_seen')
    return render(request, 'devices/device_list.html', {'devices': devices})

def device_detail(request, pk):
    device = get_object_or_404(Device, pk=pk)
    return render(request, 'devices/device_detail.html', {'device': device})
