from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta
from django.db.models import Avg
from django.db.models.functions import TruncHour
from devices.models import Device, TelemetryData
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

def dashboard_chart_data(request):
    """
    Returns aggregated telemetry data for the last 24 hours.
    Averages CPU and RAM usage per hour across all devices (or could be per device).
    For a global dashboard, global average is fine.
    """
    now = timezone.now()
    last_24h = now - timedelta(hours=24)
    
    # Aggregate by hour
    data = TelemetryData.objects.filter(timestamp__gte=last_24h) \
        .annotate(hour=TruncHour('timestamp')) \
        .values('hour') \
        .annotate(avg_cpu=Avg('cpu_usage'), avg_ram=Avg('ram_usage')) \
        .order_by('hour')
        
    labels = [entry['hour'].strftime('%H:%M') for entry in data]
    cpu_data = [round(entry['avg_cpu'], 2) for entry in data]
    ram_data = [round(entry['avg_ram'], 2) for entry in data]
    
    return JsonResponse({
        'labels': labels,
        'cpu': cpu_data,
        'ram': ram_data
    })
