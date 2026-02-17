from django.urls import path
from . import views

urlpatterns = [
    path('', views.device_list, name='device_list'),
    path('<uuid:device_id>/', views.device_detail, name='device_detail'),
    path('<uuid:device_id>/remote/', views.remote_control, name='remote_control'),
    path('<uuid:device_id>/command/', views.device_send_command, name='device_send_command'),
]
