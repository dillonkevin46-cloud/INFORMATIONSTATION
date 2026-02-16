from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from devices.models import Device
from tickets.models import Ticket

# @login_required # Commented out for now to allow viewing without login setup
def dashboard_view(request):
    device_count = Device.objects.count()
    online_count = Device.objects.filter(is_online=True).count()
    offline_count = device_count - online_count
    ticket_count = Ticket.objects.exclude(status='closed').count()
    
    recent_devices = Device.objects.order_by('-last_seen')[:10]

    context = {
        'device_count': device_count,
        'online_count': online_count,
        'offline_count': offline_count,
        'ticket_count': ticket_count,
        'recent_devices': recent_devices,
    }
    return render(request, 'core/dashboard.html', context)
