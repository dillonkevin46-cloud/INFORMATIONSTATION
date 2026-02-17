from rest_framework import viewsets
from .models import Device
from .serializers import DeviceSerializer
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
import json

class DeviceViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows devices to be viewed or edited.
    """
    # Optimized to fix N+1 query issue for telemetry data
    queryset = Device.objects.all().prefetch_related('telemetry').order_by('-created_at')
    serializer_class = DeviceSerializer

def device_list(request):
    devices = Device.objects.all().order_by('-last_seen')
    return render(request, 'devices/device_list.html', {'devices': devices})

def device_detail(request, device_id):
    device = get_object_or_404(Device, id=device_id)
    return render(request, 'devices/device_detail.html', {'device': device})

def device_send_command(request, device_id):
    if request.method == 'POST':
        try:
            device = get_object_or_404(Device, id=device_id)
            data = json.loads(request.body)
            command = data.get('command')

            if not command:
                return JsonResponse({'status': 'error', 'message': 'No command provided'}, status=400)

            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"device_{device.id}",
                {
                    "type": "device.command",
                    "content": {
                        "type": "command",
                        "command": command
                    }
                }
            )
            return JsonResponse({'status': 'success', 'message': f'Command "{command}" sent'})
        except Exception as e:
             return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'error', 'message': 'Invalid method'}, status=405)
