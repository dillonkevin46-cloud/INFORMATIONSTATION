from rest_framework import viewsets
from .models import Device, Asset
from .serializers import DeviceSerializer
from .forms import AssetForm
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
import json

class DeviceViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows devices to be viewed or edited.
    """
    queryset = Device.objects.all().order_by('-created_at')
    serializer_class = DeviceSerializer

def device_list(request):
    devices = Device.objects.all().order_by('-last_seen')
    return render(request, 'devices/device_list.html', {'devices': devices})

def device_detail(request, device_id):
    device = get_object_or_404(Device, id=device_id)
    return render(request, 'devices/device_detail.html', {'device': device})

def remote_control(request, device_id):
    device = get_object_or_404(Device, id=device_id)
    return render(request, 'devices/remote_control.html', {'device': device})

def device_send_command(request, device_id):
    # This view might still be useful for one-off commands,
    # but Remote Control page uses WebSockets directly.
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

# Asset Views
def asset_list(request):
    assets = Asset.objects.all()
    return render(request, 'devices/asset_list.html', {'assets': assets})

def asset_create(request):
    if request.method == 'POST':
        form = AssetForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('asset_list')
    else:
        form = AssetForm()
    return render(request, 'devices/asset_form.html', {'form': form, 'title': 'Create Asset'})

def asset_update(request, pk):
    asset = get_object_or_404(Asset, pk=pk)
    if request.method == 'POST':
        form = AssetForm(request.POST, instance=asset)
        if form.is_valid():
            form.save()
            return redirect('asset_list')
    else:
        form = AssetForm(instance=asset)
    return render(request, 'devices/asset_form.html', {'form': form, 'title': 'Update Asset'})
