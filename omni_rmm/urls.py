"""
URL configuration for omni_rmm project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from devices.views import DeviceViewSet
from core.views import dashboard_view, dashboard_chart_data

# API Router
router = routers.DefaultRouter()
router.register(r'devices', DeviceViewSet)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
    path("", dashboard_view, name="dashboard"),
    path("api/chart-data/", dashboard_chart_data, name="dashboard_chart_data"),
    path("devices/", include("devices.urls")),
    path("tickets/", include("tickets.urls")),
    path("knowledge-base/", include("knowledge_base.urls")),
    path("checklists/", include("checklists.urls")),
]
